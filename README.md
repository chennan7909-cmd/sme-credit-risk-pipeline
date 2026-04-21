# Real-Time Canadian SME Credit Risk Analytics Pipeline

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Apache Spark](https://img.shields.io/badge/Apache_Spark-PySpark-E25A1C?style=for-the-badge&logo=apachespark&logoColor=white)
![Apache Kafka](https://img.shields.io/badge/Apache_Kafka-Streaming-231F20?style=for-the-badge&logo=apachekafka&logoColor=white)
![XGBoost](https://img.shields.io/badge/XGBoost-ML_Model-00897B?style=for-the-badge)
![MongoDB](https://img.shields.io/badge/MongoDB-NoSQL-47A248?style=for-the-badge&logo=mongodb&logoColor=white)
![Optuna](https://img.shields.io/badge/Optuna-HPO-4B8BBE?style=for-the-badge)

**MBAI 5110G — Big Data System Design · Ontario Tech University · Winter 2026**  
*Nan Chen · Student ID: 101021912*

</div>

---

## Executive Summary

> A production-grade **Lambda Architecture** pipeline that ingests 2.26 million Lending Club loan records, trains an XGBoost credit risk model with Bayesian hyperparameter optimization, and scores live applications via a simulated Kafka → Spark Structured Streaming pipeline — all stored in MongoDB for real-time reporting. Designed to mirror the architecture used by Canadian fintech lenders such as **Borrowell** and **Uplinq** under Canada's Open Banking framework.

---

## Business Problem

Canadian SMEs represent **98%+ of all businesses** and **68% of private-sector employment**, yet credit underwriting remains slow and paper-driven. This project answers:

- Which industries and regions carry the highest default risk?
- Can year-over-year credit quality deterioration be detected automatically?
- How do you score a new loan application in **real time** with model drift alerts?

---

## Key Results at a Glance

| Metric | Value | Benchmark | Status |
|--------|-------|-----------|--------|
| AUC-ROC | **0.7009** | > 0.75 | Near Pass |
| KS Statistic | **0.2928** | > 0.30 | Near Pass |
| 5-Fold CV AUC (± std) | **0.7009 ± 0.0011** | Low variance | Pass |
| Gini Coefficient | **0.4019** | > 0.50 | Near Pass |
| Optimal Threshold | **0.172** | FN:FP = 5:1 | Applied |
| Total Expected Loss (batch) | **$845,129,230** | Basel II EL = PD×LGD×EAD | Computed |
| Streaming records scored | **500 / 500** | 100% throughput | Pass |
| High/Critical risk flagged | **174 (34.8%)** | — | Flagged |
| Drift alerts fired | **6 / 10 batches** | KS threshold = 0.10 | Retraining signal |

---

## Architecture: Lambda Pattern

```
┌─────────────────────────────────────────────────────────────────────┐
│                        LAMBDA ARCHITECTURE                          │
├─────────────────┬───────────────────────────┬───────────────────────┤
│   BATCH LAYER   │       SPEED LAYER          │    SERVING LAYER      │
│                 │                           │                       │
│  Apache Spark   │  Kafka (simulated)        │     MongoDB           │
│  (PySpark)      │  +                        │  (mongomock)          │
│                 │  Spark Structured         │                       │
│  • Ingest CSV   │  Streaming                │  • Batch aggregates   │
│  • Clean/EDA    │                           │  • Real-time scores   │
│  • Window fns   │  • Real-time inference    │  • Drift logs         │
│  • XGBoost      │  • KS drift detection     │  • EL by state        │
│  • Parquet out  │  • Watermark handling     │                       │
└─────────────────┴───────────────────────────┴───────────────────────┘
         ↑                    ↑                         ↑
   2.26M records          500 live apps           Unified queries
   (1.3M retained)       in 10 micro-batches      & reporting
```

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Distributed Processing | **Apache Spark (PySpark)** | DataFrame API, Window functions, ML pipeline |
| Streaming | **Kafka (simulated) + Spark Structured Streaming** | Real-time loan scoring, watermark handling |
| ML Model | **XGBoost + Optuna (Bayesian HPO)** | Credit default prediction, 20-trial TPE search |
| Explainability | **SHAP** | Regulatory-grade feature attribution |
| Encoding | **WoE / Information Value** | Credit industry standard categorical encoding |
| Serving | **MongoDB (mongomock)** | Flexible NoSQL document store |
| Storage | **Parquet (simulated HDFS)** | Columnar, production-grade persistence |
| Environment | **Google Colab** | Full pipeline execution, Drive-mounted dataset |

---

## Repository Structure

```
 sme-credit-risk-pipeline/
├──  Individual_Big_Data_Project_Nan_Chen_101021912.ipynb   # Full pipeline notebook
├──  Individual_Project_Report_Chen_101021912.pdf           # Technical report
├──  outputs/
│   ├── batch_dashboard.png          # 9-panel visualization dashboard
│   ├── shap_explainability.png      # SHAP beeswarm + bar chart
│   └── xgb_credit_risk.json        # Saved XGBoost model
└──  README.md
```

> **Dataset**: [Lending Club Loan Dataset (2007–2018Q4)](https://www.kaggle.com/datasets/wordsforthewise/lending-club) — 2.26M records, 151 columns, sourced from Kaggle. Not included in repo due to size (1.67 GB). Mount to Google Drive before running.

---

## Window Function Analyses

Three business-critical Spark Window operations were implemented:

### 1. `rank()` + `percent_rank()` — Geographic Risk Ranking
Ranked all US states by default rate. Top findings:

| Rank | State | Default Rate | Avg Credit Score |
|------|-------|-------------|-----------------|
| 1 | Mississippi (MS) | **26.08%** | 693.7 |
| 2 | Nebraska (NE) | 25.18% | 694.6 |
| 3 | Arkansas (AR) | 24.09% | 696.8 |
| 4 | Alabama (AL) | 23.63% | 695.6 |

→ Southeast/lower Midwest states dominate high-risk tiers, enabling **state-specific rate adjustments**.

### 2. `lag()` — Year-over-Year Default Rate Trend
Detected credit cycle dynamics per loan grade:
- **Grade A**: Spiked from 1.75% (2007) → 6.71% (2009) during the financial crisis
- **Grade B**: Deteriorated from 13.03% (2015) → 16.11% (2016) — a 3.08pp YoY signal

→ Provides **early-warning signals** impossible to detect with static snapshots.

### 3. `percent_rank()` + `avg()` — Within-Grade Borrower Percentile
Assigned each borrower a credit score percentile within their loan grade. Identified borrowers with **high credit percentile but elevated interest rates** — a fair lending compliance flag.

---

## Model Pipeline

```
Raw CSV (2.26M records)
    ↓  Filter: Fully Paid / Charged Off only
1,345,350 records retained  (default rate: 19.96%)
    ↓  Feature Engineering (4 derived features)
    ↓  WoE Encoding (province, loan_purpose, loan_grade)
    ↓  VIF Pruning (removed: credit_score, int_rate, risk_score_proxy, revol_util, delinq_2yr)
9 Features remaining
    ↓  Optuna HPO — 20 trials, 200K subsample, TPE sampler
Best CV AUC: 0.6983
    ↓  Train final XGBoost on 1,076,280 records
    ↓  Evaluate on 269,070 test records
AUC-ROC: 0.7009  |  KS: 0.2928  |  EL: $845M
```

**Optimal XGBoost hyperparameters:**
```python
n_estimators      = 223
max_depth         = 3
learning_rate     = 0.0445
subsample         = 0.672
colsample_bytree  = 0.849
min_child_weight  = 8
gamma             = 0.712
tree_method       = 'hist'
```

---

## Real-Time Streaming Results

```
Producer  →  500 loan applications  →  Kafka topic
Consumer  →  10 micro-batches (50 records each)  →  XGBoost inference  →  MongoDB

Batch #01 | high-risk=21 | avg_prob=0.503 | avg_EL=$3,399 | KS=0.165  [DRIFT ALERT]
Batch #02 | high-risk=14 | avg_prob=0.428 | avg_EL=$3,296 | KS=0.116  [DRIFT ALERT]
Batch #04 | high-risk=12 | avg_prob=0.421 | avg_EL=$2,653 | KS=0.165  [DRIFT ALERT]
...
Batch #09 | high-risk=19 | avg_prob=0.465 | avg_EL=$3,058 | KS=0.065  [OK]
Batch #10 | high-risk=18 | avg_prob=0.482 | avg_EL=$3,383 | KS=0.097  [OK]

Streaming complete: 500 records | produced: 500 | consumed: 500 | pending: 0
```

**Top 5 States by Streaming Expected Loss:**

| State | Total EL (500 records) |
|-------|----------------------|
| California | $235,554 |
| New York | $149,362 |
| Florida | $107,409 |
| Texas | $100,418 |
| New Jersey | $82,492 |

---

## SHAP Explainability

Top features by mean |SHAP| value (regulatory-grade interpretability):

```
loan_grade_woe        ████████████████████████████████  0.65   (dominant)
loan_to_revenue_ratio ████████                           0.15
province_woe          ████                               0.08
revenue_per_employee  ███                                0.06
open_accounts         ██                                 0.04
years_in_business     ██                                 0.03
```

Loan grade WoE is the single strongest predictor — consistent with credit industry intuition.

---

## Design Decisions & Production Considerations

| Decision | Rationale |
|---------|-----------|
| **Kafka simulated via Python queue** | Google Colab does not support a live broker; interface contract preserved for drop-in replacement |
| **mongomock instead of Atlas** | Full API compatibility; production swap requires one config change |
| **200K subsample for HPO** | Balanced Optuna compute time vs. search quality on Colab |
| **VIF > 10 pruning** | Eliminated multicollinearity that destabilizes XGBoost coefficient attribution |
| **WoE encoding over label encoding** | Captures log-odds relationship; industry standard for scorecards |
| **FN:FP cost ratio = 5:1** | Missing a default costs 5× more than a false alarm — threshold tuned accordingly |
| **KS drift threshold = 0.10** | Triggers retraining pipeline when score distribution shifts materially |

---

## ▶ How to Run

1. **Clone the repo**
```bash
git clone https://github.com/<your-username>/sme-credit-risk-pipeline.git
```

2. **Download the dataset** from [Kaggle](https://www.kaggle.com/datasets/wordsforthewise/lending-club) and upload `accepted_2007_to_2018Q4.csv` to your Google Drive.

3. **Open in Google Colab** and mount your Drive:
```python
from google.colab import drive
drive.mount('/content/drive')
```

4. **Run all cells** in order. The notebook installs all dependencies automatically.

> Full pipeline runtime: ~45–60 minutes on Colab (batch training dominates)

---

## Future Work

- [ ] Replace mongomock with **MongoDB Atlas** for cloud persistence
- [ ] Integrate **Apache Flink** for stateful stream processing
- [ ] Add **MLflow** experiment tracking for Optuna trial history
- [ ] Expand feature set with **bureau data** to push AUC > 0.75
- [ ] Deploy as a **REST API** (FastAPI + Docker) for live lender integration
- [ ] Automate retraining trigger when KS drift > 0.10 for 3 consecutive batches

---

## References

- Lending Club Dataset: [Kaggle](https://www.kaggle.com/datasets/wordsforthewise/lending-club)
- Basel II Expected Loss Framework: BIS (2006)
- SHAP: Lundberg & Lee (2017) — *A Unified Approach to Interpreting Model Predictions*
- Optuna: Akiba et al. (2019) — *Optuna: A Next-generation Hyperparameter Optimization Framework*
- Canada Open Banking Advisory Committee Final Report (2023)

---

<div align="center">

*Built with Apache Spark · XGBoost · Kafka · MongoDB · Optuna · SHAP*  
*Ontario Tech University · MBAI 5110G Big Data System Design · Winter 2026*

</div>
