#!/usr/bin/env python3
"""
Trust Percolation Bound — Benchmark Simulation v1

Single question: does a lean model produce a visible regime shift
in cascade exposure as trust dependence becomes sufficiently connected?

Model:
  - Network G_I (trust intermediation graph)
  - Each edge carries trust stock I_e, initially I_0
  - Shock: one node fails, all its edges removed
  - Cascade: adjacent edges lose factor (1-rho) per adjacent failure
  - Edges dropping below tau fail and propagate
  - With rho=0.3, tau=0.55: single hit survives, double hit cascades
  - Cascade size: pairs connected before shock but not after

Control parameter: Molloy-Reed branching factor
  B = (⟨k²⟩ - ⟨k⟩) / ⟨k⟩
  Giant component onset at B = 1.
"""

import numpy as np
import networkx as nx
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from collections import Counter
import time
import warnings
warnings.filterwarnings('ignore')

np.random.seed(42)

# ─── Parameters ──────────────────────────────────────────────
N = 400
TAU = 0.55
RHO = 0.3
I_0 = 1.0
N_GRAPHS = 25
N_SHOCKS = 15

# ─── Core Functions ──────────────────────────────────────────

def compute_B(G):
    """Molloy-Reed branching factor: (⟨k²⟩ - ⟨k⟩) / ⟨k⟩"""
    degs = np.array([d for _, d in G.degree()], dtype=float)
    km = degs.mean()
    if km == 0:
        return 0.0
    return (np.mean(degs**2) - km) / km


def giant_component_fraction(G):
    """Fraction of nodes in the largest connected component."""
    if G.number_of_nodes() == 0:
        return 0.0
    return max(len(c) for c in nx.connected_components(G)) / G.number_of_nodes()


def susceptibility(G):
    """Mean component size excluding giant component (percolation susceptibility)."""
    comps = sorted([len(c) for c in nx.connected_components(G)], reverse=True)
    if len(comps) <= 1:
        return comps[0] if comps else 0.0
    finite = np.array(comps[1:], dtype=float)
    return np.sum(finite**2) / np.sum(finite)


def count_pairs(components):
    """Total connected pairs from a list of component sets."""
    return sum(len(c) * (len(c) - 1) // 2 for c in components)


def run_cascade(G, tau=TAU, rho=RHO):
    """
    Node-failure cascade.

    1. Pick a random node, remove all its edges.
    2. Adjacent edges lose (1-rho) per adjacent failed edge.
    3. Edges dropping below tau fail and propagate.
    4. Repeat until stable.

    Returns (cascade_size, n_edges_failed, cascade_amplification).
    """
    edges = list(G.edges())
    n_edges = len(edges)
    if n_edges == 0:
        return 0, 0, 0.0

    # Pick random node with degree > 0
    nodes_with_edges = [v for v, d in G.degree() if d > 0]
    if not nodes_with_edges:
        return 0, 0, 0.0
    target = nodes_with_edges[np.random.randint(len(nodes_with_edges))]

    # Initialize trust
    trust = {}
    for u, v in edges:
        trust[(min(u, v), max(u, v))] = I_0

    # Connected pairs before
    comps_before = list(nx.connected_components(G))
    pairs_before = count_pairs(comps_before)
    if pairs_before == 0:
        return 0, 0, 0.0

    # --- Initial shock: fail all edges of target node ---
    failed = set()
    frontier = []
    for nb in G.neighbors(target):
        ek = (min(target, nb), max(target, nb))
        trust[ek] = 0.0
        failed.add(ek)
        frontier.append(ek)

    initial_failed = len(failed)
    if initial_failed == 0:
        return 0, 0, 0.0

    # --- Cascade ---
    while frontier:
        hit_count = Counter()
        for fu, fv in frontier:
            for node in (fu, fv):
                for nb in G.neighbors(node):
                    ek = (min(node, nb), max(node, nb))
                    if ek not in failed:
                        hit_count[ek] += 1

        next_frontier = []
        for ek, cnt in hit_count.items():
            trust[ek] *= (1 - rho) ** cnt
            if trust[ek] < tau:
                failed.add(ek)
                next_frontier.append(ek)
        frontier = next_frontier

    # --- Measure aftermath ---
    H = nx.Graph()
    H.add_nodes_from(G.nodes())
    for u, v in edges:
        ek = (min(u, v), max(u, v))
        if ek not in failed:
            H.add_edge(u, v)

    comps_after = list(nx.connected_components(H))
    pairs_after = count_pairs(comps_after)
    cascade_size = pairs_before - pairs_after

    # Baseline: what if we just removed the node with no cascade?
    G_no_cascade = G.copy()
    G_no_cascade.remove_node(target)
    pairs_baseline = count_pairs(list(nx.connected_components(G_no_cascade)))
    baseline_disruption = pairs_before - pairs_baseline

    amplification = cascade_size / max(baseline_disruption, 1)

    return cascade_size, len(failed), amplification


# ─── Graph Generators ────────────────────────────────────────

def make_er(n, mean_k):
    p = mean_k / (n - 1) if n > 1 else 0
    return nx.erdos_renyi_graph(n, min(p, 1.0))


def make_ba(n, mean_k):
    m = max(1, round(mean_k / 2))
    if m >= n:
        m = n - 1
    return nx.barabasi_albert_graph(n, m)


def make_modular(n, mean_k, n_comm=5):
    sz = [n // n_comm] * n_comm
    sz[-1] += n % n_comm
    cs = n // n_comm
    if cs <= 1:
        return make_er(n, mean_k)
    p_in = min(mean_k * 0.85 / max(cs - 1, 1), 1.0)
    p_out_denom = max(n - cs, 1)
    p_out = min(mean_k * 0.15 / p_out_denom, 1.0)
    probs = [[p_out] * n_comm for _ in range(n_comm)]
    for i in range(n_comm):
        probs[i][i] = p_in
    try:
        return nx.stochastic_block_model(sz, probs)
    except:
        return make_er(n, mean_k)


# ─── Sweep Engine ────────────────────────────────────────────

def sweep(mean_k_values, gen_func, n=N, n_graphs=N_GRAPHS, n_shocks=N_SHOCKS,
          label="", tau=TAU, rho=RHO):
    results = []
    for mk in mean_k_values:
        cascades = []
        amps = []
        Bs = []
        gcs = []
        chis = []
        edges_failed = []

        for _ in range(n_graphs):
            G = gen_func(n, mk)
            b = compute_B(G)
            Bs.append(b)
            gcs.append(giant_component_fraction(G))
            chis.append(susceptibility(G))

            for _ in range(n_shocks):
                cs, nf, amp = run_cascade(G, tau=tau, rho=rho)
                cascades.append(cs)
                amps.append(amp)
                edges_failed.append(nf)

        max_pairs = n * (n - 1) / 2
        results.append({
            'mean_k': mk,
            'B': np.mean(Bs),
            'B_std': np.std(Bs),
            'gc_frac': np.mean(gcs),
            'chi': np.mean(chis),
            'cascade_mean': np.mean(cascades),
            'cascade_median': np.median(cascades),
            'cascade_std': np.std(cascades),
            'cascade_frac': np.mean(cascades) / max_pairs,
            'cascade_frac_std': np.std(cascades) / max_pairs,
            'cascade_95': np.percentile(cascades, 95) / max_pairs,
            'amplification': np.mean(amps),
            'edges_failed_mean': np.mean(edges_failed),
        })
        if label:
            print(f"  [{label}] mean_k={mk:.1f}  B={results[-1]['B']:.2f}  "
                  f"gc={results[-1]['gc_frac']:.2f}  "
                  f"E[|C|/pairs]={results[-1]['cascade_frac']:.4f}  "
                  f"amp={results[-1]['amplification']:.2f}")
    return results


# ─── Plotting Style ──────────────────────────────────────────

def setup_style():
    plt.rcParams.update({
        'font.family': 'serif',
        'font.size': 11,
        'axes.linewidth': 0.8,
        'axes.grid': True,
        'grid.alpha': 0.3,
        'grid.linewidth': 0.5,
        'figure.facecolor': 'white',
    })

setup_style()

BLUE = '#2166AC'
RED = '#B2182B'
GREEN = '#1B7837'
ORANGE = '#D95F02'
GRAY = '#636363'

# ═══════════════════════════════════════════════════════════════
# PLOT 1: MONEY PLOT
# ═══════════════════════════════════════════════════════════════

print("=" * 60)
print("TRUST PERCOLATION BOUND — BENCHMARK SIMULATION")
print(f"N={N}  tau={TAU}  rho={RHO}  I_0={I_0}")
print(f"graphs/point={N_GRAPHS}  shocks/graph={N_SHOCKS}")
print("=" * 60)

K_VALUES = np.linspace(0.5, 6.0, 28)

print("\n--- Plot 1: Money Plot (ER) ---")
t0 = time.time()
er_results = sweep(K_VALUES, make_er, label="ER")
print(f"  Done in {time.time()-t0:.1f}s")

Bs = [r['B'] for r in er_results]
cascade_frac = [r['cascade_frac'] for r in er_results]
cascade_frac_std = [r['cascade_frac_std'] for r in er_results]
cascade_95 = [r['cascade_95'] for r in er_results]

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 9), height_ratios=[3, 1.2])

# Top: cascade exposure
ci_lo = [max(0, c - 1.96*s/np.sqrt(N_GRAPHS*N_SHOCKS))
         for c, s in zip(cascade_frac, cascade_frac_std)]
ci_hi = [c + 1.96*s/np.sqrt(N_GRAPHS*N_SHOCKS)
         for c, s in zip(cascade_frac, cascade_frac_std)]

ax1.fill_between(Bs, ci_lo, ci_hi, alpha=0.15, color=BLUE)
ax1.plot(Bs, cascade_frac, 'o-', color=BLUE, linewidth=2, markersize=4,
         label='E[cascade fraction]', zorder=5)
ax1.plot(Bs, cascade_95, '--', color=BLUE, alpha=0.5, linewidth=1,
         label='95th percentile')

# Verification cost curves
B_arr = np.array(Bs)
for beta, ls, lbl, alpha_line in [
    (0, '--', r'$C_{\mathrm{verify}}$ (flat, $\beta$=0)', 0.8),
    (0.5, '-.', r'$C_{\mathrm{verify}}$ (sublinear, $\beta$=0.5)', 0.7),
    (1.0, ':', r'$C_{\mathrm{verify}}$ (linear, $\beta$=1)', 0.6)
]:
    # Scale to intersect cascade curve at a plausible point
    c0 = 0.005
    c1 = 0.003
    cv = c0 + c1 * B_arr**beta
    ax1.plot(Bs, cv, ls, color=RED, linewidth=1.8, alpha=alpha_line, label=lbl)

ax1.axvline(x=1.0, color=GRAY, linestyle='--', alpha=0.6, linewidth=1)
ax1.text(1.05, ax1.get_ylim()[1]*0.9 if ax1.get_ylim()[1] > 0 else 0.01,
         'B=1\n(percolation)', fontsize=9, color=GRAY, va='top')

ax1.set_ylabel('Normalized cascade exposure / Verification cost', fontsize=11)
ax1.set_title(f'Trust Percolation Bound — Money Plot\n'
              f'ER graph, n={N}, τ={TAU}, ρ={RHO}', fontsize=13)
ax1.legend(fontsize=9, loc='upper left')
ax1.set_xlim(0, max(Bs) + 0.2)

# Bottom: cascade amplification
amps = [r['amplification'] for r in er_results]
ax2.bar(Bs, amps, width=0.15, color=BLUE, alpha=0.6)
ax2.axhline(y=1.0, color=GRAY, linestyle='-', alpha=0.4)
ax2.axvline(x=1.0, color=GRAY, linestyle='--', alpha=0.6, linewidth=1)
ax2.set_xlabel('Molloy-Reed branching factor B', fontsize=11)
ax2.set_ylabel('Cascade\namplification', fontsize=10)
ax2.set_xlim(0, max(Bs) + 0.2)

plt.tight_layout()
plt.savefig('/home/claude/plot1_money.png', dpi=150, bbox_inches='tight')
plt.close()
print("  Plot 1 saved.")

# ═══════════════════════════════════════════════════════════════
# PLOT 2: THRESHOLD DECOMPOSITION
# ═══════════════════════════════════════════════════════════════

print("\n--- Plot 2: Threshold Decomposition ---")

fig, axes = plt.subplots(3, 1, figsize=(10, 10), sharex=True)

# Panel 1: Giant component fraction
gc = [r['gc_frac'] for r in er_results]
axes[0].plot(Bs, gc, 'o-', color=GREEN, linewidth=2, markersize=4)
axes[0].axvline(x=1.0, color=GRAY, linestyle='--', alpha=0.6)
axes[0].set_ylabel('Giant component\nfraction', fontsize=11)
axes[0].set_title(f'Threshold Decomposition (ER, n={N})', fontsize=13)
axes[0].text(1.05, 0.5, 'connectivity\nthreshold', fontsize=9, color=GRAY)

# Panel 2: Susceptibility (proxy for coordination overhead)
chi_vals = [r['chi'] for r in er_results]
axes[1].plot(Bs, chi_vals, 's-', color=ORANGE, linewidth=2, markersize=4)
axes[1].axvline(x=1.0, color=GRAY, linestyle='--', alpha=0.6)
axes[1].set_ylabel('Susceptibility χ\n(coordination\noverhead proxy)', fontsize=11)

# Panel 3: Cascade exposure
axes[2].plot(Bs, cascade_frac, 'o-', color=BLUE, linewidth=2, markersize=4)
axes[2].fill_between(Bs, ci_lo, ci_hi, alpha=0.15, color=BLUE)
axes[2].axvline(x=1.0, color=GRAY, linestyle='--', alpha=0.6)
axes[2].set_ylabel('Cascade\nexposure', fontsize=11)
axes[2].set_xlabel('Molloy-Reed branching factor B', fontsize=11)

plt.tight_layout()
plt.savefig('/home/claude/plot2_decomposition.png', dpi=150, bbox_inches='tight')
plt.close()
print("  Plot 2 saved.")

# ═══════════════════════════════════════════════════════════════
# PLOT 3: TOPOLOGY COMPARISON
# ═══════════════════════════════════════════════════════════════

print("\n--- Plot 3: Topology Comparison ---")
K_TOPO = np.linspace(1.0, 6.0, 18)

print("  Running BA sweep...")
t0 = time.time()
ba_results = sweep(K_TOPO, make_ba, label="BA")
print(f"  Done in {time.time()-t0:.1f}s")

print("  Running Modular sweep...")
t0 = time.time()
mod_results = sweep(K_TOPO, make_modular, label="MOD")
print(f"  Done in {time.time()-t0:.1f}s")

# Also run ER on same K range
print("  Running ER sweep (topo range)...")
t0 = time.time()
er_topo = sweep(K_TOPO, make_er, label="ER-topo")
print(f"  Done in {time.time()-t0:.1f}s")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))

# Left: cascade exposure vs mean degree (showing topology matters)
for res, color, marker, label in [
    (er_topo, BLUE, 'o', 'Erdős–Rényi'),
    (ba_results, RED, 's', 'Barabási–Albert (scale-free)'),
    (mod_results, GREEN, '^', 'Modular (SBM)'),
]:
    mk = [r['mean_k'] for r in res]
    cf = [r['cascade_frac'] for r in res]
    ax1.plot(mk, cf, f'{marker}-', color=color, linewidth=2, markersize=5, label=label)

ax1.set_xlabel('Mean degree ⟨k⟩', fontsize=11)
ax1.set_ylabel('Cascade exposure (fraction of pairs)', fontsize=11)
ax1.set_title('Topology Effect: Same Mean Degree,\nDifferent Cascade Exposure', fontsize=12)
ax1.legend(fontsize=10)

# Right: cascade exposure vs B (should collapse or separate informatively)
for res, color, marker, label in [
    (er_topo, BLUE, 'o', 'Erdős–Rényi'),
    (ba_results, RED, 's', 'Barabási–Albert'),
    (mod_results, GREEN, '^', 'Modular (SBM)'),
]:
    bb = [r['B'] for r in res]
    cf = [r['cascade_frac'] for r in res]
    ax2.plot(bb, cf, f'{marker}-', color=color, linewidth=2, markersize=5, label=label)

ax2.axvline(x=1.0, color=GRAY, linestyle='--', alpha=0.6)
ax2.set_xlabel('Molloy-Reed branching factor B', fontsize=11)
ax2.set_ylabel('Cascade exposure (fraction of pairs)', fontsize=11)
ax2.set_title('Same Data Plotted Against B\n(Does B Unify the Topologies?)', fontsize=12)
ax2.legend(fontsize=10)

plt.tight_layout()
plt.savefig('/home/claude/plot3_topology.png', dpi=150, bbox_inches='tight')
plt.close()
print("  Plot 3 saved.")

# ═══════════════════════════════════════════════════════════════
# PLOT 4: RELIABILITY ROBUSTNESS
# ═══════════════════════════════════════════════════════════════

print("\n--- Plot 4: Reliability Robustness ---")
# Fix B well above threshold, vary rho (contagion strength = proxy for system fragility)
# Lower rho = edges are more "reliable" / resilient to neighbor failures

RHO_VALUES = [0.15, 0.20, 0.25, 0.30, 0.35, 0.40]
FIXED_K = 4.0  # well above percolation

fig, ax = plt.subplots(1, 1, figsize=(8, 5.5))

for rho_val in RHO_VALUES:
    print(f"  rho={rho_val}...")
    # Sweep mean_k for this rho
    K_REL = np.linspace(1.0, 6.0, 16)
    res = sweep(K_REL, make_er, n_graphs=15, n_shocks=12, rho=rho_val, label=f"rho={rho_val}")
    bb = [r['B'] for r in res]
    cf = [r['cascade_frac'] for r in res]
    ax.plot(bb, cf, 'o-', linewidth=1.8, markersize=4, label=f'ρ={rho_val}')

ax.axvline(x=1.0, color=GRAY, linestyle='--', alpha=0.6)
ax.set_xlabel('Molloy-Reed branching factor B', fontsize=11)
ax.set_ylabel('Cascade exposure (fraction of pairs)', fontsize=11)
ax.set_title(f'Reliability Robustness: Cascade Exposure Across\n'
             f'Contagion Strengths (ER, n={N}, τ={TAU})', fontsize=12)
ax.legend(fontsize=9, title='Contagion strength')

plt.tight_layout()
plt.savefig('/home/claude/plot4_reliability.png', dpi=150, bbox_inches='tight')
plt.close()
print("  Plot 4 saved.")

# ═══════════════════════════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("RESULTS SUMMARY")
print("=" * 60)

# Find approximate governance switch for ER (where cascade crosses a threshold)
print("\nER Cascade Exposure by B:")
for r in er_results:
    marker = ""
    if abs(r['B'] - 1.0) < 0.15:
        marker = " <-- near percolation threshold"
    print(f"  B={r['B']:.2f}  cascade_frac={r['cascade_frac']:.5f}  "
          f"amp={r['amplification']:.2f}  chi={r['chi']:.1f}{marker}")

print("\nTopology comparison at mean_k=4.0:")
for label, res in [("ER", er_topo), ("BA", ba_results), ("Modular", mod_results)]:
    # Find result closest to mean_k=4.0
    closest = min(res, key=lambda r: abs(r['mean_k'] - 4.0))
    print(f"  {label:10s}: B={closest['B']:.2f}  "
          f"cascade_frac={closest['cascade_frac']:.5f}  "
          f"amp={closest['amplification']:.2f}")

print(f"\nAll plots saved to /home/claude/plot*.png")
print("Done.")
