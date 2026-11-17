"""MMC-01 section 7 gates. Each returns PASS / CONDITIONAL / FAIL with the
numbers that produced the call. Gates 0, 1, 3 and 4 run before unsealing.
"""
import numpy as np


def gate0_module_viability(modules):
    """Every module >=15 genes, two-source minimum, after mapping and LCC filter.
    FAIL if fewer than three modules survive."""
    detail = {}
    survivors = []
    for mid, m in modules.items():
        n = len(m["genes_in_lcc"])
        ok = n >= 15
        detail[mid] = {
            "genes_declared": m["n_declared"],
            "genes_after_two_source_rule": m["n_two_source"],
            "genes_after_hgnc_mapping": m["n_mapped"],
            "genes_in_lcc": n,
            "mapping_loss_fraction": m["mapping_loss"],
            "mapping_loss_flagged_over_10pct": m["mapping_loss"] > 0.10,
            "meets_15_gene_minimum": ok,
        }
        if ok:
            survivors.append(mid)
    verdict = "PASS" if len(survivors) == len(modules) else (
        "CONDITIONAL" if len(survivors) >= 3 else "FAIL")
    return {"verdict": verdict, "surviving_modules": survivors,
            "n_surviving": len(survivors), "per_module": detail,
            "rule": "all modules >=15 genes -> PASS; >=3 survive -> CONDITIONAL; <3 -> FAIL"}


def gate1_target_coverage(targets):
    """At least 12 of 16 protectants with mapped targets in the LCC.
    CONDITIONAL if median direction coverage < 0.5."""
    import statistics
    mapped = {d: v for d, v in targets.items() if v["n_targets_in_lcc"] > 0}
    covs = [v["direction_coverage"] for v in mapped.values()]
    median_cov = statistics.median(covs) if covs else 0.0
    if len(mapped) < 12:
        verdict = "FAIL"
    elif median_cov < 0.5:
        verdict = "CONDITIONAL"
    else:
        verdict = "PASS"
    return {
        "verdict": verdict,
        "n_protectants_mapped_in_lcc": len(mapped),
        "n_protectants_total": len(targets),
        "median_direction_coverage": round(median_cov, 3),
        "direction_coverage_per_drug": {d: v["direction_coverage"] for d, v in targets.items()},
        "dropped_zero_targets": [d for d, v in targets.items() if v["n_targets_in_lcc"] == 0],
        "rule": ">=12 of 16 mapped -> PASS; median direction coverage <0.5 -> CONDITIONAL",
        "note": "CONDITIONAL here must be stated as a primary limitation",
    }


def _top_quartile_cut(all_z):
    """Top quartile of proximity = most negative quartile (closer = more negative)."""
    return float(np.percentile(np.asarray(all_z, dtype=float), 25))


def gate3_positive_control(z_lookup, all_z):
    """Dexrazoxane vs M1 must fall in the top quartile of all computed z-scores.
    Designed to kill the study."""
    z = z_lookup.get(("dexrazoxane", "M1"))
    cut = _top_quartile_cut(all_z)
    if z is None:
        return {"verdict": "FAIL", "reason": "dexrazoxane-M1 z not computed"}
    passed = z <= cut
    ranks = np.sort(np.asarray(all_z, dtype=float))
    pctile = float((ranks < z).sum()) / len(ranks) * 100.0
    return {
        "verdict": "PASS" if passed else "FAIL",
        "dexrazoxane_M1_z": round(float(z), 4),
        "top_quartile_cutoff_z": round(cut, 4),
        "percentile_of_all_z": round(pctile, 1),
        "n_z_scores_in_reference_set": len(all_z),
        "rule": "z <= 25th percentile of all computed z-scores",
        "note": "FAIL means stop and write up the negative methods finding. "
                "Do not adjust the module, threshold or metric to rescue it.",
    }


def gate4_negative_controls(neg_z_lookup, all_z, negative_controls, modules):
    """No negative-control drug may score in the top quartile against any module.
    One violation CONDITIONAL, two or more FAIL."""
    cut = _top_quartile_cut(all_z)
    violations = []
    for d in negative_controls:
        for mid in modules:
            z = neg_z_lookup.get((d, mid))
            if z is not None and z <= cut:
                violations.append({"drug": d, "module": mid, "z": round(float(z), 4)})
    def grade(n):
        return "PASS" if n == 0 else ("CONDITIONAL" if n == 1 else "FAIL")

    n_pairs = len(violations)
    n_drugs = len({v["drug"] for v in violations})
    return {
        # The protocol sentence is ambiguous about the unit of a "violation":
        # "No negative-control drug may score in the top quartile against any
        # module. One violation is CONDITIONAL... two or more is FAIL."
        # Counting drug-module pairs and counting distinct drugs give different
        # verdicts here. Both are reported; neither was pre-specified, so the
        # stricter reading is carried as the headline verdict.
        "verdict": grade(n_pairs),
        "verdict_by_drug_module_pair": grade(n_pairs),
        "verdict_by_distinct_drug": grade(n_drugs),
        "n_violations_pairs": n_pairs,
        "n_violations_distinct_drugs": n_drugs,
        "violations": violations,
        "top_quartile_cutoff_z": round(cut, 4),
        "rule": "0 violations PASS; 1 CONDITIONAL; >=2 FAIL",
        "ambiguity_note": "unit of 'violation' not pre-specified; stricter "
                          "(pair-counting) reading taken as the headline verdict",
    }


def gate2_evaluable_pairs(n_evaluable):
    """At least 8 protectant-toxicant pairs with extractable trial evidence.
    Runs after the commitment."""
    verdict = "PASS" if n_evaluable >= 8 else "FAIL"
    return {
        "verdict": verdict,
        "n_evaluable_pairs": n_evaluable,
        "rule": ">=8 evaluable pairs; below 8 the study is descriptive only "
                "(no p-value, no classification performance)",
    }
