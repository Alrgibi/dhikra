#!/usr/bin/env python3
"""revise2.py -- class 2 remainder (heading punctuation) and the last class-3 leftover."""
from revlib import rep, write

HEADS = [
 ("chapter4.md", "### 4.3.1 The Stimulus Is Not The One The Model Was Calibrated On, And What That Costs",
                 "### 4.3.1 The Stimulus Is Not The One The Model Was Calibrated On And What That Costs"),
 ("chapter5.md", "### 5.5.1 The Information-Unit Scorer, Checked Against A Human", "### 5.5.1 The Information Unit Scorer Checked Against A Human"),
 ("chapter5.md", "## 5.6 Multi-Task Analysis", "## 5.6 Analysis Across Tasks"),
 ("chapter5.md", "## 5.8 The Fifteen Negative Results, In One Place", "## 5.8 The Fifteen Negative Results In One Place"),
 ("chapter5.md", "### 5.9.1 Test-Retest Stability And The Minimal Detectable Change", "### 5.9.1 Visit To Visit Stability And The Minimal Detectable Change"),
 ("chapter5.md", "### 5.10.1 The Referential Deficit Index, Probed In English", "### 5.10.1 The Referential Deficit Index Probed In English"),
 ("chapter5.md", "## 5.12 Cross-Corpus Transfer", "## 5.12 Transfer Between Corpora"),
 ("chapter5.md", "## 5.18 Control-Referenced Thresholding", "## 5.18 Control Referenced Thresholding"),
 ("chapter5.md", "## 5.20 Banded Reporting And Decision-Curve Analysis", "## 5.20 Banded Reporting And Decision Curve Analysis"),
 ("chapter5.md", "## 5.23 A Minimum-Length Rule Does Not Fix Specificity", "## 5.23 A Minimum Length Rule Does Not Fix Specificity"),
 ("chapter5.md", "## 5.29 The Age-Adjusted Posterior And Discrimination", "## 5.29 The Age Adjusted Posterior And Discrimination"),
 ("appendix_a.md", "## A.1 Lexical, Syntactic And Fluency Features", "## A.1 Lexical Syntactic And Fluency Features"),
 ("appendix_a.md", "## A.2 Information-Content Features", "## A.2 Information Content Features"),
 ("appendix_a.md", "## A.3 Discourse-Semantic Features", "## A.3 Discourse Semantic Features"),
 ("appendix_c.md", "## C.2 Training Data, Features And Exclusions", "## C.2 The Training Data The Features And The Exclusions"),
 ("appendix_e.md", "## E.3 The Age-Adjusted Result", "## E.3 The Age Adjusted Result"),
 ("appendix_e.md", "## E.7 What The Demonstration Shows, And Does Not", "## E.7 What The Demonstration Shows And Does Not"),
 ("appendix_g.md", "## G.4 What It Costs, Measured", "## G.4 What It Costs As Measured"),
 ("appendix_h.md", "## H.2 Age-Band Prevalence", "## H.2 Age Band Prevalence"),
 ("appendix_h.md", "## H.3 The Retained Multiplier, ×2.5", "## H.3 The Retained Multiplier Of 2.5"),
 ("appendix_h.md", "## H.4 The Removed Multiplier, ×4.0", "## H.4 The Removed Multiplier Of 4.0"),
 ("appendix_h.md", "## H.6 The Age-Flatness Measurement", "## H.6 The Age Flatness Measurement"),
 ("appendix_h.md", "## H.7 Diagnosis One — The Tokenisation Defect", "## H.7 Diagnosis One The Tokenisation Defect"),
 ("appendix_h.md", "## H.8 Diagnosis Two — The Comparison Defect", "## H.8 Diagnosis Two The Comparison Defect"),
 ("appendix_i.md", "## I.2 The Battery, Instantiated For Libya", "## I.2 The Battery Instantiated For Libya"),
 ("appendix_i.md", "## I.4 Marker Families By Target, And The Minimal Probe", "## I.4 Marker Families By Target And The Minimal Probe"),
]
for f, a, b in HEADS:
    rep(f, a + "\n", b + "\n")
# D.2 "STARD-AI" is the guideline's registered name; the hyphen is part of the name and is kept (reported).

# class 3 leftover: the sentence that named the retired claim now names the record instead
rep("chapter3.md", "it is not a defence, and it does not restore the retired claim that the corpus was never seen.",
    "it is not a defence, and it does not shorten the exposure history recorded in section 3.9.")

write("revise2: ")
