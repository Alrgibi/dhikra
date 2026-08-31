"""
model.py
--------
Training and evaluation for the ذِكرى screening classifier.

DESIGN PRINCIPLES (these are what make the results defensible in a viva)

 1. NO DATA LEAKAGE. Imputation and scaling are fitted INSIDE each
    cross-validation fold via an sklearn Pipeline, never on the full dataset.
    Scaling before splitting is the single most common way undergraduate ML
    results become silently inflated.

 2. CLINICAL METRICS, NOT JUST ACCURACY. A screening tool is judged on
    sensitivity (of the people who are impaired, how many did we catch?) and
    specificity (of the healthy, how many did we correctly clear?). Accuracy
    alone hides a model that simply predicts the majority class. ROC-AUC is
    reported as a threshold-independent summary.

 3. STRATIFIED, REPEATED CROSS-VALIDATION. Datasets in this field are small
    (the ADReSS benchmark is ~156 recordings). A single train/test split gives
    an unstable estimate, so repeated stratified k-fold is used and the mean
    with standard deviation is reported.

 4. MODEL COMPARISON. Several classifier families are compared rather than one
    being asserted. Interpretable models (logistic regression) are included
    deliberately -- in a clinical screening context an explainable model that
    performs comparably is preferable to an opaque one.
"""
from __future__ import annotations
import numpy as np
import pandas as pd

from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.model_selection import (RepeatedStratifiedKFold, cross_validate,
                                     StratifiedKFold, cross_val_predict,
                                     StratifiedGroupKFold)
from sklearn.metrics import (confusion_matrix, roc_auc_score,
                             classification_report)
from sklearn.inspection import permutation_importance


# ------------------------------------------------------------- models ----
def build_models(random_state: int = 42,
                 balanced: bool = True) -> dict[str, Pipeline]:
    """
    Each model is wrapped in a leakage-free preprocessing pipeline.

    CLASS BALANCING (balanced=True by default)
    After participant matching the recording counts are uneven, because control
    participants happen to contribute more repeat visits. An unweighted model
    then drifts toward predicting the majority class, which shows up as high
    specificity and poor SENSITIVITY -- it clears healthy people confidently
    while missing patients. For a screening instrument that failure mode is the
    wrong way round: the cost of missing a case far exceeds the cost of an
    unnecessary referral. Class weighting restores the balance.
    """
    cw = "balanced" if balanced else None
    def wrap(clf):
        return Pipeline([
            ("impute", SimpleImputer(strategy="median")),
            ("scale", StandardScaler()),
            ("clf", clf),
        ])

    return {
        "Logistic Regression": wrap(LogisticRegression(
            max_iter=5000, C=1.0, class_weight=cw, random_state=random_state)),
        "Logistic Regression (L1)": wrap(LogisticRegression(
            max_iter=5000, penalty="l1", solver="liblinear", C=0.5,
            class_weight=cw, random_state=random_state)),
        "SVM (RBF)": wrap(SVC(
            kernel="rbf", C=1.0, probability=True, class_weight=cw,
            random_state=random_state)),
        "Random Forest": wrap(RandomForestClassifier(
            n_estimators=500, min_samples_leaf=2, class_weight=cw,
            random_state=random_state)),
        "Gradient Boosting": wrap(GradientBoostingClassifier(
            random_state=random_state)),
    }


# --------------------------------------------------------- evaluation ----
def _sensitivity_specificity(y_true, y_pred):
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    sens = tp / (tp + fn) if (tp + fn) else float("nan")   # recall, impaired
    spec = tn / (tn + fp) if (tn + fp) else float("nan")   # recall, control
    return sens, spec, (tn, fp, fn, tp)


def evaluate_models(X: pd.DataFrame, y: np.ndarray, n_splits: int = 5,
                    n_repeats: int = 10, random_state: int = 42,
                    groups: np.ndarray | None = None) -> pd.DataFrame:
    """
    Repeated stratified k-fold evaluation of every model.

    `groups` (participant ids) MUST be supplied for longitudinal corpora such
    as Pitt, where one person contributes several yearly recordings. Without
    grouping, the same participant can appear in both the training and test
    folds, letting the model identify the individual rather than the disease
    and inflating every reported metric. When groups are given, all recordings
    from one participant stay together in the same fold.

    Returns a tidy DataFrame, one row per model, sorted by ROC-AUC.
    """
    if groups is not None:
        cv = StratifiedGroupKFold(n_splits=n_splits, shuffle=True,
                                  random_state=random_state)
    else:
        cv = RepeatedStratifiedKFold(n_splits=n_splits, n_repeats=n_repeats,
                                     random_state=random_state)
    scoring = {
        "accuracy": "accuracy",
        "roc_auc": "roc_auc",
        "sensitivity": "recall",                    # recall of the positive class
        "specificity": "recall_macro",              # replaced below by explicit calc
        "f1": "f1",
        "precision": "precision",
    }
    rows = []
    for name, pipe in build_models(random_state).items():
        res = cross_validate(pipe, X, y, cv=cv, scoring=scoring,
                             groups=groups, n_jobs=-1, error_score="raise")
        # explicit specificity via out-of-fold predictions
        if groups is not None:
            cv_single = StratifiedGroupKFold(n_splits=n_splits, shuffle=True,
                                             random_state=random_state)
        else:
            cv_single = StratifiedKFold(n_splits=n_splits, shuffle=True,
                                        random_state=random_state)
        y_oof = cross_val_predict(pipe, X, y, cv=cv_single, groups=groups,
                                  n_jobs=-1)
        sens, spec, cm = _sensitivity_specificity(y, y_oof)
        rows.append({
            "model": name,
            "accuracy": res["test_accuracy"].mean(),
            "accuracy_sd": res["test_accuracy"].std(),
            "roc_auc": res["test_roc_auc"].mean(),
            "roc_auc_sd": res["test_roc_auc"].std(),
            "sensitivity": sens,
            "specificity": spec,
            "f1": res["test_f1"].mean(),
            "precision": res["test_precision"].mean(),
            "confusion(tn,fp,fn,tp)": cm,
        })
    return (pd.DataFrame(rows)
            .sort_values("roc_auc", ascending=False)
            .reset_index(drop=True))


# ------------------------------------------------------ explainability ----
def explain_model(pipe: Pipeline, X: pd.DataFrame, y: np.ndarray,
                  top_n: int = 15, random_state: int = 42) -> pd.DataFrame:
    """
    Permutation importance: how much does performance drop when each feature is
    shuffled? Model-agnostic, and it answers the question a clinician actually
    asks -- 'which speech measures drove this result?'
    """
    pipe.fit(X, y)
    r = permutation_importance(pipe, X, y, n_repeats=20,
                               random_state=random_state, scoring="roc_auc",
                               n_jobs=-1)
    imp = (pd.DataFrame({
                "feature": X.columns,
                "importance": r.importances_mean,
                "sd": r.importances_std})
           .sort_values("importance", ascending=False)
           .reset_index(drop=True))
    return imp.head(top_n)


def linear_coefficients(pipe: Pipeline, X: pd.DataFrame, y: np.ndarray,
                        top_n: int = 15) -> pd.DataFrame:
    """
    Signed, standardised coefficients from a linear model -- these give
    DIRECTION as well as magnitude ('more pausing -> higher risk'), which is
    what makes a screening result explainable to a non-engineer.
    """
    pipe.fit(X, y)
    clf = pipe.named_steps["clf"]
    if not hasattr(clf, "coef_"):
        raise TypeError("model has no linear coefficients")
    coefs = clf.coef_.ravel()
    df = pd.DataFrame({"feature": X.columns, "coefficient": coefs})
    df["abs"] = df["coefficient"].abs()
    return (df.sort_values("abs", ascending=False)
              .drop(columns="abs").head(top_n).reset_index(drop=True))


def report(pipe: Pipeline, X: pd.DataFrame, y: np.ndarray,
           n_splits: int = 5, random_state: int = 42) -> str:
    """Full out-of-fold classification report for one model."""
    cv = StratifiedKFold(n_splits=n_splits, shuffle=True,
                         random_state=random_state)
    y_pred = cross_val_predict(pipe, X, y, cv=cv, n_jobs=-1)
    y_prob = cross_val_predict(pipe, X, y, cv=cv, method="predict_proba",
                               n_jobs=-1)[:, 1]
    sens, spec, (tn, fp, fn, tp) = _sensitivity_specificity(y, y_pred)
    lines = [
        classification_report(y, y_pred,
                              target_names=["Control", "Impaired"], digits=3),
        f"ROC-AUC     : {roc_auc_score(y, y_prob):.3f}",
        f"Sensitivity : {sens:.3f}   (impaired correctly identified)",
        f"Specificity : {spec:.3f}   (controls correctly cleared)",
        f"Confusion   : TN={tn}  FP={fp}  FN={fn}  TP={tp}",
    ]
    return "\n".join(lines)


def screening_threshold(y_true, y_prob, min_sensitivity: float = 0.85):
    """
    Choose the decision threshold for SCREENING use.

    The default 0.5 cut-off maximises overall accuracy, which is the wrong
    objective here: a screening test exists to avoid missing cases, and a
    missed patient costs far more than an unnecessary referral to a clinician
    who will assess them properly anyway. The threshold is therefore set to the
    highest value that still achieves the required sensitivity, which maximises
    specificity subject to that clinical constraint.

    Returns (threshold, sensitivity, specificity).

    NOTE ON THE DEFAULT (recorded 2026-08-22): the deployed operating
    threshold 0.367 was produced with min_sensitivity=0.75, passed explicitly
    (confirmed in docs/RECONSTRUCTION.md sect 2.8; full floor sweep in
    results/reconstruction/sensitivity_floor_sweep.json — at this function's
    0.85 default the same OOF vector would give threshold 0.304 with 63
    healthy referrals per 100). The 0.85 default predates the development
    choice of 0.75 and is retained unchanged so existing callers behave
    identically; do not read the default as the deployed floor.
    """
    import numpy as np
    ths = np.unique(np.round(y_prob, 3))
    best = (0.5, 0.0, 0.0)
    for th in ths:
        pred = (y_prob >= th).astype(int)
        tn, fp, fn, tp = confusion_matrix(y_true, pred, labels=[0, 1]).ravel()
        sens = tp / (tp + fn) if (tp + fn) else 0.0
        spec = tn / (tn + fp) if (tn + fp) else 0.0
        if sens >= min_sensitivity and spec > best[2]:
            best = (float(th), float(sens), float(spec))
    return best
