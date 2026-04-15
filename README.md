# The Trust Percolation Bound

**"The Trust Percolation Bound: Correlated Trust Failure and the Structural Limits of Trust Governance"**

Amadeus Brandes, Independent Researcher, Kronberg, Germany

arXiv: [XXXX.XXXXX](https://arxiv.org/abs/XXXX.XXXXX) (physics.soc-ph; cross-listed cs.SI, econ.TH)

---

## Overview

Trust-based governance fails not because bilateral trust erodes, but because trust failures become correlated through the network's local structure. This paper models trust as accumulated evidence and motivates a cascade rule from Bayesian posterior contamination. It proves an exact analytic floor for cascade initiation and demonstrates that, in the intermediate contagion regime, the cascade phase transition requires persistent local clustering — a structural prerequisite absent from standard random-graph benchmarks but present in many real coordination networks.

The paper identifies an endogenous structural tension in trust governance: the shared-contact topology that makes distributed trust coordination efficient is also the topology that, under sufficient contagion sensitivity and connectivity, makes correlated trust failure possible.

**Proposition 1.** Under a single-node shock with uniform initial trust stocks, no secondary trust failure can occur if contagion sensitivity ρ ≤ 1 − √τ, regardless of network structure.

**Clustering prerequisite.** In the intermediate contagion regime (1 − √τ < ρ ≤ 1 − τ), the cascade phase transition requires persistent local clustering. On locally tree-like networks (ER, configuration model), cascades vanish with system size. On networks with fixed clustering (Watts–Strogatz), the transition is sharp, sharpens with *n*, and sits at the analytic floor.

**Empirical anchor.** The global clinical trial system is used as an empirical anchor. A sponsor–sponsor projection of the site–sponsor bipartite network (ClinicalTrials.gov, Phase III oncology, 2022–present) yields: mean degree ⟨k⟩ ≈ 66.6, Molloy–Reed branching factor B ≈ 154, average clustering C ≈ 0.77 (global transitivity 0.48), and a giant component covering 98.4% of connected sponsors.

## Repository Structure

```
paper/
  brandes_tpb_2026.tex           # LaTeX submission file (23 references)

figures/
  prop1_verification.png         # Fig 1: Proposition 1 across 13 τ values
  fss_ws_profiles.png            # Fig 2: WS cascade profiles, 4 system sizes
  fss_ws_vs_er.png               # Fig 3: WS vs ER contrast + ER detail
  step3_overlay.png              # Fig 4: Multiplicative vs additive rules
  fss_peaks_and_clustering.png   # Fig 5: Peak exposure and clustering vs n

simulations/
  tpb_figures_pub.py             # Publication figure generation (final)
  tpb_propositions.py            # Proposition 1 verification + topology comparison
  tpb_corrected.py               # Corrected phase boundary with CI
  tpb_benchmark.py               # Core benchmark (v1, retained)
  tpb_network_projection.py      # Sponsor-sponsor projection analysis

data/
  tpb_clinical_trials_query.py   # ClinicalTrials.gov API query (run in Colab)
  tpb_network_projection.py      # Sponsor-sponsor projection (run in Colab)
```

## Reproducing the Results

Requirements: Python 3.8+, `numpy`, `networkx`, `matplotlib`.

```bash
pip install numpy networkx matplotlib

# Publication figures (Figures 1–5)
python simulations/tpb_figures_pub.py
```

Runtime: ~10–15 minutes. WS simulations use 500 cascade runs per ρ point at n = 250, decreasing to 20 at n = 2000.

The clinical trial data scripts (`data/`) query the ClinicalTrials.gov API and require an internet connection. They are designed to run in Google Colab.

## Key Parameters

| Parameter | Value | Meaning |
|-----------|-------|---------|
| τ | 0.55 | Coordination threshold |
| ρ_min | 0.2584 | Analytic cascade floor (= 1 − √τ) |
| ⟨k⟩ | 6 | Mean degree (WS/ER benchmarks) |
| n | 250–2000 | System sizes (finite-size scaling) |
| WS p | 0.1 | Rewiring probability (clustering ≈ 0.45) |

## Data Sources

- **ClinicalTrials.gov API v2**: Phase III oncology trials, 2022–present (2,312 trials, 830 sponsors, 44,913 sites)
- **AACT Database** (CTTI): facility_investigators table for investigator overlap analysis
- Sponsor–sponsor projection statistics computed from ClinicalTrials.gov data

## Citation

```bibtex
@article{brandes2026tpb,
  author  = {Brandes, Amadeus},
  title   = {The Trust Percolation Bound: Correlated Trust Failure and the Structural Limits of Trust Governance},
  year    = {2026},
  note    = {arXiv:XXXX.XXXXX [physics.soc-ph]}
}
```

## License

MIT

## Contact

Amadeus Brandes — [ORCID 0009-0009-9902-2587](https://orcid.org/0009-0009-9902-2587)
