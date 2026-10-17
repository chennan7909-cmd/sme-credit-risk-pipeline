# Analytical review and boundaries

The original notebook and PDF are preserved as historical coursework. This change
adds a separate SQL reporting layer; it does not silently replace stored model
outputs or claim that the model has been retrained.

## Issues identified in the original implementation

1. **Population and feature semantics.** US personal-loan fields were renamed as
   Canadian SME attributes. This does not create SME evidence. The correct mappings
   are documented in the metric dictionary; do not interpret revenue-per-employee
   or years-in-business features literally.
2. **Outcome selection and vintages.** Only resolved statuses entered the notebook
   aggregates. Later vintages have different resolution coverage. Their apparent
   improvement is not evidence of better underwriting. New SQL retains unresolved
   loans and reports coverage, but cannot reconstruct fixed-horizon event histories.
3. **Leakage.** Median imputation and target-based WoE encoding occur before the
   train/test split. WoE therefore uses holdout labels. Encoding must be fit inside
   each training fold in a future retraining workflow.
4. **Test-set reuse.** The test set is used for early stopping and threshold
   selection. A future model needs separate training, validation and untouched
   out-of-time test cohorts. Original AUC 0.7009 is a historical result, not a clean
   prospective performance estimate.
5. **Probability and expected loss.** Class weighting changes the score probability
   interpretation; calibration is not established. Fixed LGD 45% and original
   principal as exposure are assumptions. The reported USD 845M is an illustrative
   score-based sum on the test subset, not booked loss, savings or regulatory EL.
6. **Threshold costs.** Minimizing FPR + 5×FNR weights conditional error rates. It is
   not equivalent to FP count + 5×FN count unless prevalence is included. The stored
   0.172 threshold must not be described as a validated economic optimum.
7. **Streaming scope.** The speed layer uses a Python queue, manual micro-batches
   and mongomock. It is not a running Kafka broker, Spark Structured Streaming job
   or production MongoDB deployment. KS alerts in batches of 50 do not establish
   degradation or justify automatic retraining on their own.
8. **Interpretation.** State differences do not justify state-specific pricing.
   Pricing outliers do not establish unfair treatment. Compare grade, term, vintage
   and other relevant factors, consider uncertainty, and obtain appropriate review
   before any operational decision. VIF pruning is not required for tree models,
   and SHAP plots alone do not establish regulatory compliance.

## What this iteration establishes

Executable descriptive SQL, explicit metric denominators, coverage checks,
traceable saved results and proposed next decisions. It does not establish causal
product impact, production readiness, Canadian SME model validity, dbt experience,
user conversion, revenue, approval rates, or a live business deployment.

## Next analytical work with the full dataset

- Re-run SQL on the original CSV and investigate all exclusions; compare to legacy
  aggregates without requiring exact agreement across different cleaning contracts.
- Compare purpose and state signals within grade × term × issue vintage, retaining
  unresolved shares and sample counts; add uncertainty before ranking review actions.
- Obtain dated outcomes and snapshot metadata before estimating fixed-horizon
  vintage risk. A/B experiments are not possible from this accepted-loan dataset.
- If extending ML, fix the semantic and split issues first, then evaluate calibration
  and workload/cost tradeoffs on untouched later-vintage data.
