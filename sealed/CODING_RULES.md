# MMC-01 — Outcome coding rules (fixed before outcomes.json was written)

These operationalise section 8 of the protocol. They were written before the pair
table was assembled and are applied mechanically. Every judgement call that these
rules did not fully determine is logged in the `notes` field of the pair record.

## Eligibility

- **R1.** A pair (protectant x module) is *evaluable* if at least one prospective
  randomised controlled trial randomised that protectant against placebo/control,
  in patients receiving the module's index agent class as cardiotoxic therapy, and
  reported a cardiac outcome.
- **R2.** Trial arms that randomise a **combination of two separately listed
  protectants** (OVERCOME: enalapril + carvedilol; Cardiac CARE: candesartan +
  carvedilol) are not attributable to either single drug. They are recorded but
  do not establish or code a pair. Sacubitril/valsartan is exempt: section 5
  declares it a single combination entry.
- **R3.** Subgroup-only evidence does not establish a pair (e.g. the prior-
  anthracycline subgroup of Guglin 2019). Recorded, not coded.
- **R9.** Module assignment: assign the module whose index agent **all**
  participants received. If participants received index agents of two modules,
  assign to the module the trial names as its toxicity of interest. If the trial
  names both, the pair is **ambiguous** and is excluded from the primary analysis
  and recorded separately.

## Coding

- **R4.** Code at the trial's own stated **primary** cardiac endpoint, at its
  pre-specified primary timepoint. Extended-follow-up reports of the same trial
  do not override the primary report; they are recorded.
- **R5.** Pair with several qualifying RCTs: all significant-favourable on their
  own primary -> POSITIVE; all non-significant -> NULL; disagreement -> MIXED.
- **R6.** Pair with one qualifying RCT: significant-favourable on its primary ->
  POSITIVE if a meta-analysis including it is directionally concordant, else
  MIXED; non-significant -> NULL.
- **R8.** Primary endpoint non-significant but a prespecified secondary or
  surrogate cardiac endpoint significant-favourable -> MIXED, not NULL.
  (Section 8: "significant only on a secondary or surrogate endpoint".)
- **R7.** `endpoint_type` records `clinical_events`, `lvef_ctrcd`, or
  `surrogate_subclinical` (GLS, troponin, strain). Sensitivity analysis 4 of
  section 9 drops `surrogate_subclinical`. This flag does not change the code.

## Fixed before counting

MIXED pairs are excluded from the primary analysis (section 8). Sensitivity
analysis 3 bounds them as NULL and as POSITIVE. This was fixed by the protocol
before the pair table existed and is not revisited.

## Residual integrity weakness (recorded, not resolved)

The protocol's seal prevents outcome knowledge from reaching the *graph*. It does
not prevent it from reaching the *modules*, because the same analyst builds both
and builds outcomes first by design. Section 2.1 is therefore enforced by the
commitment hash and by the two-source module rule, not by blinding. This is a
strengthening of pre-specified limitation 7, not a new limitation.
