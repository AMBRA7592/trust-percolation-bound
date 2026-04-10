# The Trust Percolation Bound

Companion code and figures for:

**"The Trust Percolation Bound: Correlated Trust Failure and the Topology of Governance Transitions"**
Amadeus Brandes, April 2026

## Overview

Trust-based governance fails not because bilateral trust erodes, but because trust failures become correlated. This paper derives an exact analytic floor for cascade initiation and demonstrates a sharp phase boundary in the space of network connectivity and contagion sensitivity.

**Proposition 1.** Under a single-node shock, no secondary trust failure can occur if contagion sensitivity ρ ≤ 1 − √τ, regardless of network structure.

**Benchmark Result 1.** The materiality boundary ρ*(B) converges to the analytic floor as effective connectivity B increases.

**Benchmark Result 2.** Effective connectivity governs cascade onset; network topology governs cascade severity conditional on onset.

## Repository Structure

```
paper/
  tpb_paper_draft_v1.md       # Full paper draft

figures/
  fig1_initiation_floor.png   # Proposition 1 verification across 12 τ values
  fig2_phase_boundary.png     # ρ*(B) with 95% bootstrap CI
  fig3_phase_space.png        # Full (⟨k⟩, ρ) phase space heatmap
  fig4_cascade_profiles.png   # Net secondary cascade profiles at fixed B

simulations/
  tpb_benchmark.py            # Core benchmark: money plot, threshold decomposition,
                               # topology comparison, reliability robustness
  tpb_propositions.py         # Proposition 1 verification, B-matched topology
                               # comparison, publication heatmap
  tpb_corrected.py            # Corrected fine boundary using net secondary
                               # exposure with bootstrap CI
```

## Reproducing the Results

Requirements: Python 3.8+, `numpy`, `networkx`, `matplotlib`.

```bash
pip install numpy networkx matplotlib

# Core benchmark (produces plots 1-4 from the initial sweep)
python simulations/tpb_benchmark.py

# Proposition 1 verification + B-matched topology comparison
python simulations/tpb_propositions.py

# Corrected phase boundary with confidence intervals
python simulations/tpb_corrected.py
```

Each script is self-contained and produces figures in the working directory. Runtime is 2–5 minutes per script on a standard machine.

## Parameters

All simulations use the following benchmark configuration unless otherwise noted:

| Parameter | Value | Meaning |
|-----------|-------|---------|
| n | 250 | Number of agents |
| I₀ | 1.0 | Initial trust stock per edge |
| τ | 0.55 | Coordination threshold |
| ρ | swept | Contagion sensitivity |
| ρ_min | 0.2584 | Analytic cascade floor (= 1 − √τ) |

## Key Finding

The cascade initiation floor ρ_min = 1 − √τ is exact: below it, zero net secondary cascade on any graph. Above it, the materiality boundary converges to the floor as effective connectivity increases — producing a sharp governance transition concentrated in a vanishingly narrow parameter band at high connectivity.

## License

MIT

## Contact

Amadeus Brandes — [amadeusbrandes on arXiv](https://arxiv.org/search/?searchtype=author&query=amadeusbrandes)
