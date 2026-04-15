#!/usr/bin/env python3
"""
Trust Percolation Bound — Publication-Quality Figure Generation
Regenerates all 5 main-text figures with polished styling.
Runtime: ~10-15 minutes.
"""

import numpy as np
import networkx as nx
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from collections import Counter
import time
import warnings
warnings.filterwarnings('ignore')

np.random.seed(42)

# ═══════════════════════════════════════════════════════════════
# PUBLICATION STYLE
# ═══════════════════════════════════════════════════════════════

plt.rcParams.update({
    'font.family': 'serif',
    'font.serif': ['Computer Modern Roman', 'DejaVu Serif', 'Times New Roman'],
    'font.size': 14,
    'axes.labelsize': 16,
    'axes.titlesize': 16,
    'legend.fontsize': 13,
    'xtick.labelsize': 13,
    'ytick.labelsize': 13,
    'axes.linewidth': 1.0,
    'xtick.major.width': 0.8,
    'ytick.major.width': 0.8,
    'xtick.major.size': 5,
    'ytick.major.size': 5,
    'xtick.minor.size': 3,
    'ytick.minor.size': 3,
    'figure.facecolor': 'white',
    'axes.facecolor': 'white',
    'axes.grid': False,
    'savefig.dpi': 200,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.15,
})

# Color palette
BLUE = '#2166AC'
RED = '#B2182B'
GREEN = '#1B7837'
ORANGE = '#D95F02'
GRAY = '#636363'
LIGHTGRAY = '#CCCCCC'

OUT = '/home/claude'

# ═══════════════════════════════════════════════════════════════
# CORE CASCADE FUNCTIONS
# ═══════════════════════════════════════════════════════════════

I_0 = 1.0
TAU = 0.55
RHO_MIN = 1 - np.sqrt(TAU)

def count_pairs(components):
    return sum(len(c) * (len(c) - 1) // 2 for c in components)

def run_cascade(G, n, tau, rho, rule='mult'):
    edges = list(G.edges())
    if not edges:
        return 0.0
    nodes_with_edges = [v for v, d in G.degree() if d > 0]
    if not nodes_with_edges:
        return 0.0
    target = nodes_with_edges[np.random.randint(len(nodes_with_edges))]
    trust = {(min(u,v), max(u,v)): I_0 for u,v in edges}
    comps_before = list(nx.connected_components(G))
    pairs_before = count_pairs(comps_before)
    if pairs_before == 0:
        return 0.0

    failed = set()
    frontier = []
    for nb in G.neighbors(target):
        ek = (min(target, nb), max(target, nb))
        trust[ek] = 0.0
        failed.add(ek)
        frontier.append(ek)
    if not failed:
        return 0.0

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
            if rule == 'mult':
                trust[ek] *= (1 - rho) ** cnt
            else:  # additive
                trust[ek] = max(0, trust[ek] - rho * cnt)
            if trust[ek] < tau:
                failed.add(ek)
                next_frontier.append(ek)
        frontier = next_frontier

    H = nx.Graph()
    H.add_nodes_from(G.nodes())
    for u, v in edges:
        ek = (min(u,v), max(u,v))
        if ek not in failed:
            H.add_edge(u, v)
    pairs_after = count_pairs(list(nx.connected_components(H)))
    total_disruption = pairs_before - pairs_after
    max_pairs = n * (n - 1) / 2

    G2 = G.copy()
    G2.remove_node(target)
    baseline = pairs_before - count_pairs(list(nx.connected_components(G2)))
    net_secondary = max(0, total_disruption - baseline)
    return net_secondary / max_pairs

def make_er(n, mean_k):
    p = mean_k / (n - 1) if n > 1 else 0
    return nx.erdos_renyi_graph(n, min(p, 1.0))

def make_ws(n, k, p):
    return nx.watts_strogatz_graph(n, k, p)


# ═══════════════════════════════════════════════════════════════
# FIGURE 1: PROPOSITION 1 VERIFICATION
# ═══════════════════════════════════════════════════════════════

print("=" * 60)
print("FIGURE 1: Proposition 1 Verification")
print("=" * 60)

TAU_VALUES = np.linspace(0.2, 0.8, 13)
RHO_FINE = np.linspace(0.05, 0.55, 26)
MEAN_K_HIGH = 5.5
N_GRAPHS_PROP = 15
N_SHOCKS_PROP = 10
N_PROP = 250

analytic_rho_min = []
empirical_rho_min = []

for tau in TAU_VALUES:
    rho_analytic = 1 - np.sqrt(tau)
    analytic_rho_min.append(rho_analytic)
    found = False
    for rho in RHO_FINE:
        amps = []
        for _ in range(N_GRAPHS_PROP):
            G = make_er(N_PROP, MEAN_K_HIGH)
            for _ in range(N_SHOCKS_PROP):
                # Quick amplification check
                edges = list(G.edges())
                if not edges:
                    continue
                nodes_we = [v for v, d in G.degree() if d > 0]
                if not nodes_we:
                    continue
                target = nodes_we[np.random.randint(len(nodes_we))]
                trust = {(min(u,v), max(u,v)): I_0 for u,v in edges}
                comps_before = list(nx.connected_components(G))
                pairs_before = count_pairs(comps_before)
                if pairs_before == 0:
                    continue
                failed = set()
                frontier = []
                for nb in G.neighbors(target):
                    ek = (min(target, nb), max(target, nb))
                    trust[ek] = 0.0
                    failed.add(ek)
                    frontier.append(ek)
                while frontier:
                    hc = Counter()
                    for fu, fv in frontier:
                        for node in (fu, fv):
                            for nb in G.neighbors(node):
                                ek2 = (min(node, nb), max(node, nb))
                                if ek2 not in failed:
                                    hc[ek2] += 1
                    nf = []
                    for ek2, cnt in hc.items():
                        trust[ek2] *= (1 - rho) ** cnt
                        if trust[ek2] < tau:
                            failed.add(ek2)
                            nf.append(ek2)
                    frontier = nf
                H = nx.Graph()
                H.add_nodes_from(G.nodes())
                for u, v in edges:
                    ek2 = (min(u,v), max(u,v))
                    if ek2 not in failed:
                        H.add_edge(u, v)
                pa = count_pairs(list(nx.connected_components(H)))
                td = pairs_before - pa
                G2 = G.copy()
                G2.remove_node(target)
                bl = pairs_before - count_pairs(list(nx.connected_components(G2)))
                amp = td / max(bl, 1)
                amps.append(amp)
        mean_amp = np.mean(amps) if amps else 0
        if mean_amp > 1.5:
            empirical_rho_min.append(rho)
            found = True
            print(f"  τ={tau:.2f}  analytic={rho_analytic:.4f}  empirical≈{rho:.3f}")
            break
    if not found:
        empirical_rho_min.append(np.nan)

fig, ax = plt.subplots(1, 1, figsize=(8, 5.5))

tau_smooth = np.linspace(0.15, 0.85, 200)
rho_smooth = 1 - np.sqrt(tau_smooth)
ax.plot(tau_smooth, rho_smooth, '-', color=RED, linewidth=2.5,
        label=r'Analytic floor: $\rho_{\min} = 1 - \sqrt{\tau}$', zorder=5)
ax.plot(TAU_VALUES, empirical_rho_min, 'o', color=BLUE, markersize=9,
        markeredgecolor='white', markeredgewidth=0.8,
        label=r'Empirical onset (amplification $> 1.5\times$)', zorder=6)

ax.fill_between(tau_smooth, rho_smooth, 0.6, alpha=0.06, color=RED)
ax.fill_between(tau_smooth, 0, rho_smooth, alpha=0.06, color=BLUE)

ax.text(0.55, 0.42, 'Cascades\npossible', fontsize=15, color=RED,
        fontweight='bold', alpha=0.4, ha='center')
ax.text(0.55, 0.10, 'No cascades\n(Proposition 1)', fontsize=15,
        color=BLUE, fontweight='bold', alpha=0.4, ha='center')

ax.set_xlabel(r'Coordination threshold $\tau$')
ax.set_ylabel(r'Contagion sensitivity $\rho$')
ax.legend(loc='upper left', framealpha=0.95, edgecolor=LIGHTGRAY)
ax.set_xlim(0.15, 0.85)
ax.set_ylim(0.0, 0.55)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.savefig(f'{OUT}/prop1_verification.png')
plt.close()
print("  → prop1_verification.png saved")


# ═══════════════════════════════════════════════════════════════
# FIGURES 2, 3, 5: FINITE-SIZE SCALING (WS + ER)
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("FIGURES 2, 3, 5: Finite-Size Scaling")
print("=" * 60)

RHO_GRID = np.concatenate([
    np.linspace(0.22, 0.255, 3),
    np.linspace(0.258, 0.32, 16),
    np.linspace(0.33, 0.42, 4),
])
RHO_GRID = np.unique(np.round(RHO_GRID, 4))

N_VALUES = [250, 500, 1000, 2000]
WS_K = 6
WS_P = 0.1
SAMPLES = {250: (10, 10), 500: (7, 7), 1000: (4, 5), 2000: (3, 4)}

COLORS_N = {250: BLUE, 500: ORANGE, 1000: GREEN, 2000: RED}
MARKERS_N = {250: 'o', 500: 's', 1000: '^', 2000: 'D'}

ws_results = {}
er_results = {}
ws_clustering = {}
er_clustering = {}

for n in N_VALUES:
    n_graphs, n_shocks = SAMPLES[n]
    t0 = time.time()

    # WS
    ws_data = []
    cc_vals = []
    for rho in RHO_GRID:
        vals = []
        for _ in range(n_graphs):
            G = make_ws(n, WS_K, WS_P)
            cc_vals.append(nx.average_clustering(G))
            for _ in range(n_shocks):
                vals.append(run_cascade(G, n, TAU, rho))
        ws_data.append(np.mean(vals))
    ws_results[n] = np.array(ws_data)
    ws_clustering[n] = np.mean(cc_vals)

    # ER
    er_data = []
    cc_vals_er = []
    for rho in RHO_GRID:
        vals = []
        for _ in range(n_graphs):
            G = make_er(n, WS_K)
            cc_vals_er.append(nx.average_clustering(G))
            for _ in range(n_shocks):
                vals.append(run_cascade(G, n, TAU, rho))
        er_data.append(np.mean(vals))
    er_results[n] = np.array(er_data)
    er_clustering[n] = np.mean(cc_vals_er)

    print(f"  n={n}: {time.time()-t0:.1f}s  WS_C={ws_clustering[n]:.3f}  ER_C={er_clustering[n]:.4f}")


# --- FIGURE 2: WS profiles ---
fig, ax = plt.subplots(1, 1, figsize=(8, 5.5))

for n in N_VALUES:
    ax.plot(RHO_GRID, ws_results[n] * 100, '-' + MARKERS_N[n],
            color=COLORS_N[n], markersize=6, markeredgecolor='white',
            markeredgewidth=0.5, linewidth=1.8,
            label=f'$n = {n}$')

ax.axvline(x=RHO_MIN, color=GRAY, linestyle='--', linewidth=1.2, alpha=0.7)
ax.text(RHO_MIN + 0.003, 85, r'$\rho_{\min}$', fontsize=14, color=GRAY,
        fontstyle='italic')

ax.set_xlabel(r'Contagion sensitivity $\rho$')
ax.set_ylabel('Net secondary cascade exposure (%)')
ax.legend(loc='center right', framealpha=0.95, edgecolor=LIGHTGRAY)
ax.set_xlim(RHO_GRID[0], RHO_GRID[-1])
ax.set_ylim(-2, 105)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.savefig(f'{OUT}/fss_ws_profiles.png')
plt.close()
print("  → fss_ws_profiles.png saved")


# --- FIGURE 3: WS vs ER side by side ---
# Use 1×4 layout instead of 2×2 for more breathing room
fig, axes = plt.subplots(1, 4, figsize=(16, 4.5), sharey=True)

for i, n in enumerate(N_VALUES):
    ax = axes[i]
    ax.plot(RHO_GRID, ws_results[n] * 100, '-o', color=BLUE,
            markersize=4, markeredgecolor='white', markeredgewidth=0.3,
            linewidth=1.8, label='WS' if i == 0 else None)
    ax.plot(RHO_GRID, er_results[n] * 100, '-s', color=RED,
            markersize=4, markeredgecolor='white', markeredgewidth=0.3,
            linewidth=1.8, label='ER' if i == 0 else None)
    ax.axvline(x=RHO_MIN, color=GRAY, linestyle='--', linewidth=1.0, alpha=0.5)
    ax.set_title(f'$n = {n}$', fontsize=14)
    ax.set_xlabel(r'$\rho$')
    ax.set_xlim(RHO_GRID[0], RHO_GRID[-1])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    if i > 0:
        ax.spines['left'].set_visible(False)
        ax.tick_params(left=False)

axes[0].set_ylabel('Net secondary cascade (%)')
axes[0].set_ylim(-2, 105)
axes[0].legend(loc='center right', framealpha=0.95, edgecolor=LIGHTGRAY,
               fontsize=13)

plt.subplots_adjust(wspace=0.08)
plt.savefig(f'{OUT}/fss_ws_vs_er.png')
plt.close()
print("  → fss_ws_vs_er.png saved")


# --- FIGURE 5: Peaks and clustering ---
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 5))

ws_peaks = [ws_results[n].max() * 100 for n in N_VALUES]
er_peaks = [er_results[n].max() * 100 for n in N_VALUES]
ws_cc = [ws_clustering[n] for n in N_VALUES]
er_cc = [er_clustering[n] for n in N_VALUES]

ax1.plot(N_VALUES, ws_peaks, '-o', color=BLUE, markersize=9,
         markeredgecolor='white', markeredgewidth=0.8, linewidth=2.2,
         label='WS')
ax1.plot(N_VALUES, er_peaks, '-s', color=RED, markersize=9,
         markeredgecolor='white', markeredgewidth=0.8, linewidth=2.2,
         label='ER')
ax1.set_xlabel('System size $n$')
ax1.set_ylabel('Peak cascade exposure (%)')
ax1.legend(framealpha=0.95, edgecolor=LIGHTGRAY)
ax1.set_ylim(-2, 105)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)

ax2.plot(N_VALUES, ws_cc, '-o', color=BLUE, markersize=9,
         markeredgecolor='white', markeredgewidth=0.8, linewidth=2.2,
         label='WS')
ax2.plot(N_VALUES, er_cc, '-s', color=RED, markersize=9,
         markeredgecolor='white', markeredgewidth=0.8, linewidth=2.2,
         label='ER')
ax2.set_xlabel('System size $n$')
ax2.set_ylabel('Clustering coefficient $C$')
ax2.legend(framealpha=0.95, edgecolor=LIGHTGRAY)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)

plt.tight_layout(w_pad=3)
plt.savefig(f'{OUT}/fss_peaks_and_clustering.png')
plt.close()
print("  → fss_peaks_and_clustering.png saved")


# ═══════════════════════════════════════════════════════════════
# FIGURE 4: MULTIPLICATIVE vs ADDITIVE
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("FIGURE 4: Cascade Rule Comparison")
print("=" * 60)

N_STEP3 = 1000
RHO_STEP3 = np.concatenate([
    np.linspace(0.18, 0.22, 3),
    np.linspace(0.225, 0.32, 20),
    np.linspace(0.33, 0.42, 4),
])
RHO_STEP3 = np.unique(np.round(RHO_STEP3, 4))

n_g, n_s = 4, 5

mult_data = []
add_data = []
for rho in RHO_STEP3:
    mv, av = [], []
    for _ in range(n_g):
        G = make_ws(N_STEP3, WS_K, WS_P)
        for _ in range(n_s):
            mv.append(run_cascade(G, N_STEP3, TAU, rho, rule='mult'))
            av.append(run_cascade(G, N_STEP3, TAU, rho, rule='add'))
    mult_data.append(np.mean(mv))
    add_data.append(np.mean(av))
    if rho % 0.05 < 0.01:
        print(f"  ρ={rho:.3f} done")

mult_data = np.array(mult_data)
add_data = np.array(add_data)

RHO_MIN_ADD = (I_0 - TAU) / 2  # = 0.225

fig, ax = plt.subplots(1, 1, figsize=(8, 5.5))

ax.plot(RHO_STEP3, mult_data * 100, '-o', color=BLUE, markersize=5,
        markeredgecolor='white', markeredgewidth=0.4, linewidth=2,
        label=r'Multiplicative: $I_e \leftarrow I_e \cdot (1-\rho)^h$')
ax.plot(RHO_STEP3, add_data * 100, '-s', color=RED, markersize=5,
        markeredgecolor='white', markeredgewidth=0.4, linewidth=2,
        label=r'Additive: $I_e \leftarrow I_e - \rho \cdot h$')

ax.axvline(x=RHO_MIN, color=BLUE, linestyle='--', linewidth=1.2, alpha=0.5)
ax.axvline(x=RHO_MIN_ADD, color=RED, linestyle='--', linewidth=1.2, alpha=0.5)

ax.text(RHO_MIN + 0.003, 75, r'$\rho_{\min}^M$', fontsize=13,
        color=BLUE, fontstyle='italic')
ax.text(RHO_MIN_ADD - 0.018, 75, r'$\rho_{\min}^A$', fontsize=13,
        color=RED, fontstyle='italic')

ax.set_xlabel(r'Contagion sensitivity $\rho$')
ax.set_ylabel('Net secondary cascade exposure (%)')
ax.legend(loc='center right', framealpha=0.95, edgecolor=LIGHTGRAY)
ax.set_xlim(RHO_STEP3[0], RHO_STEP3[-1])
ax.set_ylim(-2, 105)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.savefig(f'{OUT}/step3_overlay.png')
plt.close()
print("  → step3_overlay.png saved")


print("\n" + "=" * 60)
print("ALL FIGURES REGENERATED")
print("=" * 60)
