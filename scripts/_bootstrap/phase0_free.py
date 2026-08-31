"""PHASE 0 FREE DIAGNOSTICS -- no model fitting, no new features, no corpus movement.
Gate checks for triage items 1 (information efficiency), 2 (healthy normative
normalisation) and 5 (repeat-averaging x sex).  Everything here is computed from
feature files and stored OOF predictions that already exist in results/.
"""
import numpy as np, pandas as pd, json, os, sys
R = os.path.join(os.path.dirname(__file__), "..", "..", "results")
R = os.path.abspath(R)
rng = np.random.default_rng(42)

def auc(y, s):
    y = np.asarray(y); s = np.asarray(s, dtype=float)
    m = ~np.isnan(s)
    y, s = y[m], s[m]
    npos, nneg = int((y == 1).sum()), int((y == 0).sum())
    if npos == 0 or nneg == 0: return np.nan
    r = pd.Series(s).rank().values
    return (r[y == 1].sum() - npos * (npos + 1) / 2.0) / (npos * nneg)

# ---------- build development frame in canonical order: Pitt then Delaware ----------
pf = pd.read_csv(f"{R}/pitt_cookie/features.csv")
pm = pd.read_csv(f"{R}/pitt_cookie/meta.csv")
df_ = pd.read_csv(f"{R}/delaware/cookie_features.csv")
dm = pd.read_csv(f"{R}/delaware/cookie_meta.csv")
pm["source"] = "Pitt"; dm["source"] = "Delaware"
if "visit" not in dm.columns: dm["visit"] = 1
meta = pd.concat([pm, dm], ignore_index=True, sort=False)
feat = pd.concat([pf, df_], ignore_index=True, sort=False)
print("frame:", meta.shape, feat.shape)

oof = np.load(f"{R}/summary/oof_predictions.npy")
oly = np.load(f"{R}/summary/oof_labels.npy")
olg = np.load(f"{R}/summary/oof_source.npy", allow_pickle=True)
ogr = np.load(f"{R}/summary/oof_groups.npy", allow_pickle=True)
ok = (len(oof) == len(meta)) and bool((oly == meta["label"].values).all()) and bool((olg == meta["source"].values).all())
print("ORDER CHECK (labels+source align):", ok)
if not ok:
    print("  label mismatch count:", int((oly != meta['label'].values).sum()))
    print("  source mismatch count:", int((olg != meta['source'].values).sum()))
meta["oof"] = oof
y = meta["label"].values
sex = meta["sex"].astype(str).str.lower().str[0].values   # 'f'/'m'
src = meta["source"].values
print("sex counts:", pd.Series(sex).value_counts().to_dict())

# ================= CHECK A : information-efficiency family ==================
print("\n" + "=" * 78)
print("CHECK A  --  single-feature AUC, efficiency family vs iu.total")
print("=" * 78)
FAM = ["iu.total", "iu.per_100_words", "iu.proportion", "iu.action_object_ratio",
       "iu.subjects", "iu.actions", "iu.objects", "iu.places"]
FAM = [c for c in FAM if c in feat.columns]
rows = []
for c in FAM:
    v = feat[c].values.astype(float)
    a_all = auc(y, -v)                      # lower IU expected in impaired
    a_p = auc(y[src == "Pitt"], -v[src == "Pitt"])
    a_d = auc(y[src == "Delaware"], -v[src == "Delaware"])
    a_f = auc(y[sex == "f"], -v[sex == "f"])
    a_m = auc(y[sex == "m"], -v[sex == "m"])
    rows.append(dict(feature=c, auc_all=a_all, auc_pitt=a_p, auc_del=a_d,
                     auc_F=a_f, auc_M=a_m, sex_gap=a_f - a_m))
A = pd.DataFrame(rows).sort_values("auc_all", ascending=False)
pd.set_option("display.width", 200); pd.set_option("display.float_format", lambda x: f"{x:.4f}")
print(A.to_string(index=False))

# word count alone, as the denominator control
if "n_words" in feat.columns:
    w = feat["n_words"].values.astype(float)
elif "lex.n_words" in feat.columns:
    w = feat["lex.n_words"].values.astype(float)
else:
    w = None
if w is not None:
    print(f"\n n_words alone      : AUC(-w)={auc(y,-w):.4f}   AUC(+w)={auc(y,w):.4f}")

# bootstrap the two headline features, participant-clustered
pid = meta["participant_id"].astype(str).values
uniq = np.unique(pid)
idx_by_p = {p: np.where(pid == p)[0] for p in uniq}
def boot_gap(v, B=2000):
    out_all, out_gap = [], []
    for _ in range(B):
        pick = rng.choice(uniq, size=len(uniq), replace=True)
        ii = np.concatenate([idx_by_p[p] for p in pick])
        yy, vv, ss = y[ii], v[ii], sex[ii]
        out_all.append(auc(yy, -vv))
        out_gap.append(auc(yy[ss == "f"], -vv[ss == "f"]) - auc(yy[ss == "m"], -vv[ss == "m"]))
    return np.nanpercentile(out_all, [2.5, 97.5]), np.nanpercentile(out_gap, [2.5, 97.5])
for c in ["iu.total", "iu.per_100_words"]:
    if c in feat.columns:
        ci_a, ci_g = boot_gap(feat[c].values.astype(float))
        print(f" {c:22s} AUC 95% CI [{ci_a[0]:.4f},{ci_a[1]:.4f}]  sex-gap 95% CI [{ci_g[0]:+.4f},{ci_g[1]:+.4f}]")

# paired difference: density minus count, same bootstrap draws
if "iu.per_100_words" in feat.columns:
    v1 = feat["iu.total"].values.astype(float); v2 = feat["iu.per_100_words"].values.astype(float)
    d = []
    for _ in range(2000):
        pick = rng.choice(uniq, size=len(uniq), replace=True)
        ii = np.concatenate([idx_by_p[p] for p in pick])
        d.append(auc(y[ii], -v2[ii]) - auc(y[ii], -v1[ii]))
    d = np.array(d)
    print(f" paired delta (density - count): {np.nanmean(d):+.4f}  95% CI [{np.nanpercentile(d,2.5):+.4f},{np.nanpercentile(d,97.5):+.4f}]  P(delta>0)={np.mean(d>0):.3f}")
