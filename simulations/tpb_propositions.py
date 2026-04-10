#!/usr/bin/env python3
"""
Trust Percolation Bound — Proposition Verification & B-Matched Topology

1. Verify Proposition 1: ρ_min = 1 - √τ  (cascade initiation floor)
2. B-matched topology comparison (clean test of pure topology effect)
3. Publication-quality amplification heatmap
"""

import numpy as np
import networkx as nx
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from collections import Counter
import time
import warnings
warnings.filterwarnings('ignore')

np.random.seed(42)

# ─── Core Functions ──────────────────────────────────────────

N = 250
I_0 = 1.0

def compute_B(G):
    degs = np.array([d for _, d in G.degree()], dtype=float)
    km = degs.mean()
    if km == 0:
        return 0.0
    return (np.mean(degs**2) - km) / km

def count_pairs(components):
    return sum(len(c) * (len(c) - 1) // 2 for c in components)

def run_cascade(G, tau, rho):
    edges = list(G.edges())
    if not edges:
        return 0, 0, 0.0
    nodes_with_edges = [v for v, d in G.degree() if d > 0]
    if not nodes_with_edges:
        return 0, 0, 0.0
    target = nodes_with_edges[np.random.randint(len(nodes_with_edges))]

    trust = {}
    for u, v in edges:
        trust[(min(u, v), max(u, v))] = I_0

    comps_before = list(nx.connected_components(G))
    pairs_before = count_pairs(comps_before)
    if pairs_before == 0:
        return 0, 0, 0.0

    failed = set()
    frontier = []
    for nb in G.neighbors(target):
        ek = (min(target, nb), max(target, nb))
        trust[ek] = 0.0
        failed.add(ek)
        frontier.append(ek)

    if not failed:
        return 0, 0, 0.0

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

    H = nx.Graph()
    H.add_nodes_from(G.nodes())
    for u, v in edges:
        ek = (min(u, v), max(u, v))
        if ek not in failed:
            H.add_edge(u, v)

    pairs_after = count_pairs(list(nx.connected_components(H)))
    cascade_size = pairs_before - pairs_after
    G2 = G.copy()
    G2.remove_node(target)
    baseline = pairs_before - count_pairs(list(nx.connected_components(G2)))
    amp = cascade_size / max(baseline, 1)
    max_pairs = N * (N - 1) / 2
    return cascade_size / max_pairs, len(failed), amp


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
    p_out = min(mean_k * 0.15 / max(n - cs, 1), 1.0)
    probs = [[p_out] * n_comm for _ in range(n_comm)]
    for i in range(n_comm):
        probs[i][i] = p_in
    try:
        return nx.stochastic_block_model(sz, probs)
    except:
        return make_er(n, mean_k)


plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 11,
    'axes.linewidth': 0.8,
    'figure.facecolor': 'white',
})

BLUE = '#2166AC'
RED = '#B2182B'
GREEN = '#1B7837'
ORANGE = '#D95F02'
GRAY = '#636363'


# ═══════════════════════════════════════════════════════════════
# PART 1: PROPOSITION VERIFICATION
# ρ_min = 1 - √τ
# ═══════════════════════════════════════════════════════════════

print("=" * 60)
print("PART 1: PROPOSITION VERIFICATION — ρ_min = 1 - √τ")
print("=" * 60)

TAU_VALUES = np.linspace(0.2, 0.8, 13)
RHO_FINE = np.linspace(0.05, 0.55, 26)

# For each tau, find the empirical ρ_min where cascades first appear
# Use high-connectivity ER to ensure cascades are possible if ρ allows
MEAN_K_HIGH = 5.5
N_GRAPHS_PROP = 15
N_SHOCKS_PROP = 10

analytic_rho_min = []
empirical_rho_min = []
tau_tested = []

CASCADE_THRESHOLD = 0.015  # above mechanical node removal

for tau in TAU_VALUES:
    rho_analytic = 1 - np.sqrt(tau)
    analytic_rho_min.append(rho_analytic)

    # Find empirical floor
    found = False
    for rho in RHO_FINE:
        cascades = []
        amps = []
        for _ in range(N_GRAPHS_PROP):
            G = make_er(N, MEAN_K_HIGH)
            for _ in range(N_SHOCKS_PROP):
                cf, nf, amp = run_cascade(G, tau=tau, rho=rho)
                cascades.append(cf)
                amps.append(amp)

        mean_amp = np.mean(amps)
        if mean_amp > 1.5:  # cascades are amplifying beyond direct removal
            empirical_rho_min.append(rho)
            found = True
            print(f"  τ={tau:.2f}  analytic ρ_min={rho_analytic:.4f}  "
                  f"empirical ρ_min≈{rho:.3f}  (amp={mean_amp:.1f})")
            break

    if not found:
        empirical_rho_min.append(np.nan)
        print(f"  τ={tau:.2f}  analytic ρ_min={rho_analytic:.4f}  "
              f"empirical: no cascade found in range")

    tau_tested.append(tau)

# Plot
fig, ax = plt.subplots(1, 1, figsize=(9, 6))

ax.plot(TAU_VALUES, analytic_rho_min, '-', color=RED, linewidth=2.5,
        label=r'Analytic: $\rho_{\min} = 1 - \sqrt{\tau}$', zorder=5)
ax.plot(tau_tested, empirical_rho_min, 'o', color=BLUE, markersize=8,
        label=r'Empirical $\rho_{\min}$ (amplification > 1.5×)', zorder=6)

# Shade regions
tau_fill = np.linspace(0.15, 0.85, 100)
rho_fill = 1 - np.sqrt(tau_fill)
ax.fill_between(tau_fill, rho_fill, 0.6, alpha=0.08, color=RED)
ax.fill_between(tau_fill, 0, rho_fill, alpha=0.08, color=BLUE)

ax.text(0.55, 0.42, 'Cascades\npossible', fontsize=13, color=RED,
        fontweight='bold', alpha=0.5, ha='center')
ax.text(0.55, 0.10, 'No cascades\n(regardless of\nconnectivity)', fontsize=13,
        color=BLUE, fontweight='bold', alpha=0.5, ha='center')

ax.set_xlabel(r'Coordination threshold $\tau$', fontsize=13)
ax.set_ylabel(r'Contagion sensitivity $\rho$', fontsize=13)
ax.set_title(r'Proposition 1: Cascade Initiation Floor $\rho_{\min} = 1 - \sqrt{\tau}$'
             f'\n(ER, n={N}, ⟨k⟩={MEAN_K_HIGH})', fontsize=13)
ax.legend(fontsize=11, loc='upper left')
ax.set_xlim(0.15, 0.85)
ax.set_ylim(0, 0.6)
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('/home/claude/prop1_verification.png', dpi=150, bbox_inches='tight')
plt.close()
print("\nProposition 1 verification saved.")


# ═══════════════════════════════════════════════════════════════
# PART 2: B-MATCHED TOPOLOGY COMPARISON
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("PART 2: B-MATCHED TOPOLOGY COMPARISON")
print("=" * 60)

# Strategy: for each target B value, find the mean_k that gives
# approximately that B for each topology, then compare cascade
# exposure at matched B.

TAU = 0.55
RHO_SWEEP = np.linspace(0.20, 0.45, 11)
N_GRAPHS_B = 12
N_SHOCKS_B = 8

# First, calibrate: for each topology, find mean_k -> B mapping
print("\nCalibrating B(⟨k⟩) for each topology...")
K_CALIB = np.linspace(1.0, 8.0, 30)

def calibrate_B(gen_func, k_values, n_samples=15):
    """Return (k_values, B_values) calibration curve."""
    Bs = []
    for mk in k_values:
        b_samples = [compute_B(gen_func(N, mk)) for _ in range(n_samples)]
        Bs.append(np.mean(b_samples))
    return np.array(k_values), np.array(Bs)

er_k, er_B = calibrate_B(make_er, K_CALIB)
ba_k, ba_B = calibrate_B(make_ba, K_CALIB)
mod_k, mod_B = calibrate_B(make_modular, K_CALIB)

print(f"  ER:  B range [{er_B.min():.1f}, {er_B.max():.1f}]")
print(f"  BA:  B range [{ba_B.min():.1f}, {ba_B.max():.1f}]")
print(f"  MOD: B range [{mod_B.min():.1f}, {mod_B.max():.1f}]")

# Find overlapping B range
B_min = max(er_B.min(), mod_B.min()) + 0.5
B_max = min(er_B.max(), mod_B.max()) - 0.5
# BA has much higher B, so we compare ER vs Modular at matched B,
# and show BA separately

TARGET_Bs = np.linspace(max(B_min, 2.0), min(B_max, 6.5), 10)
print(f"\nTarget B range for ER/Modular comparison: [{TARGET_Bs[0]:.1f}, {TARGET_Bs[-1]:.1f}]")

def find_k_for_B(k_cal, B_cal, target_B):
    """Interpolate to find mean_k giving target B."""
    if target_B < B_cal.min() or target_B > B_cal.max():
        return None
    return np.interp(target_B, B_cal, k_cal)


def sweep_at_B(gen_func, target_Bs, k_cal, B_cal, rho_values, label=""):
    """For each target B, find appropriate mean_k and sweep rho."""
    results = []
    for tb in target_Bs:
        mk = find_k_for_B(k_cal, B_cal, tb)
        if mk is None:
            continue

        rho_results = []
        graphs = [gen_func(N, mk) for _ in range(N_GRAPHS_B)]
        actual_B = np.mean([compute_B(g) for g in graphs])

        for rho in rho_values:
            cascades = []
            amps = []
            for G in graphs:
                for _ in range(N_SHOCKS_B):
                    cf, nf, amp = run_cascade(G, tau=TAU, rho=rho)
                    cascades.append(cf)
                    amps.append(amp)
            rho_results.append({
                'rho': rho,
                'cascade': np.mean(cascades),
                'amp': np.mean(amps),
            })

        results.append({
            'target_B': tb,
            'actual_B': actual_B,
            'mean_k': mk,
            'rho_results': rho_results,
        })
        print(f"  [{label}] target B={tb:.1f}  actual B={actual_B:.1f}  "
              f"⟨k⟩={mk:.2f}")

    return results


print("\nSweeping ER at matched B values...")
er_matched = sweep_at_B(make_er, TARGET_Bs, er_k, er_B, RHO_SWEEP, label="ER")

print("\nSweeping Modular at matched B values...")
mod_matched = sweep_at_B(make_modular, TARGET_Bs, mod_k, mod_B, RHO_SWEEP, label="MOD")


# ═══════════════════════════════════════════════════════════════
# FIGURE: B-Matched Phase Boundary (ER vs Modular)
# ═══════════════════════════════════════════════════════════════

fig, axes = plt.subplots(1, 2, figsize=(15, 6))

# Left panel: cascade exposure vs ρ at selected matched B values
ax = axes[0]
B_show = [3.0, 4.0, 5.0, 6.0]  # B values to highlight
for tb in B_show:
    # Find closest
    er_match = min(er_matched, key=lambda r: abs(r['target_B'] - tb), default=None)
    mod_match = min(mod_matched, key=lambda r: abs(r['target_B'] - tb), default=None)

    if er_match and mod_match:
        er_rhos = [r['rho'] for r in er_match['rho_results']]
        er_cas = [r['cascade'] for r in er_match['rho_results']]
        mod_rhos = [r['rho'] for r in mod_match['rho_results']]
        mod_cas = [r['cascade'] for r in mod_match['rho_results']]

        alpha = 0.4 + 0.15 * (tb - 3.0)
        ax.plot(er_rhos, er_cas, 'o-', color=BLUE, alpha=alpha, linewidth=1.8,
                markersize=4, label=f'ER, B≈{er_match["actual_B"]:.1f}')
        ax.plot(mod_rhos, mod_cas, 's--', color=GREEN, alpha=alpha, linewidth=1.8,
                markersize=4, label=f'Mod, B≈{mod_match["actual_B"]:.1f}')

ax.axhline(y=0.03, color=GRAY, linestyle=':', alpha=0.5, linewidth=1)
ax.text(0.21, 0.035, '3% threshold', fontsize=9, color=GRAY)
ax.set_xlabel(r'Contagion sensitivity $\rho$', fontsize=12)
ax.set_ylabel('Cascade exposure (fraction of pairs)', fontsize=12)
ax.set_title('Cascade Exposure at Matched B\n(ER vs Modular)', fontsize=12)
ax.legend(fontsize=8, ncol=2, loc='upper left')
ax.grid(True, alpha=0.3)

# Right panel: critical ρ* vs B for both topologies
ax = axes[1]

CASCADE_Q = 0.03

for matched, color, marker, ls, label in [
    (er_matched, BLUE, 'o', '-', 'ER'),
    (mod_matched, GREEN, 's', '-.', 'Modular'),
]:
    Bs_plot = []
    rho_crits = []
    for r in matched:
        rho_data = r['rho_results']
        # Find first ρ where cascade > q
        for rd in rho_data:
            if rd['cascade'] >= CASCADE_Q:
                Bs_plot.append(r['actual_B'])
                rho_crits.append(rd['rho'])
                break

    if Bs_plot:
        ax.plot(Bs_plot, rho_crits, f'{marker}{ls}', color=color, linewidth=2.5,
                markersize=7, label=label)

# Analytic floor
ax.axhline(y=1-np.sqrt(TAU), color=RED, linestyle='--', linewidth=1.5, alpha=0.7,
           label=r'$\rho_{\min} = 1 - \sqrt{\tau}$')

ax.set_xlabel(r'Molloy-Reed branching factor $B$', fontsize=12)
ax.set_ylabel(r'Critical contagion sensitivity $\rho^*$', fontsize=12)
ax.set_title(f'Phase Boundary at Matched B\n'
             f'(≥{CASCADE_Q:.0%} cascade exposure, τ={TAU})', fontsize=12)
ax.legend(fontsize=11)
ax.grid(True, alpha=0.3)

# Annotate
ax.text(3.5, 0.40, 'Cascade-\nexposed', fontsize=12, color=RED,
        fontweight='bold', alpha=0.4, ha='center')
ax.text(5.5, 0.22, 'Trust-\nviable', fontsize=12, color=BLUE,
        fontweight='bold', alpha=0.4, ha='center')

plt.tight_layout()
plt.savefig('/home/claude/b_matched_comparison.png', dpi=150, bbox_inches='tight')
plt.close()
print("\nB-matched comparison saved.")


# ═══════════════════════════════════════════════════════════════
# PART 3: REFINED AMPLIFICATION HEATMAP (ER)
# Higher resolution, publication style
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("PART 3: REFINED AMPLIFICATION HEATMAP")
print("=" * 60)

K_FINE = np.linspace(1.0, 6.5, 18)
RHO_FINE2 = np.linspace(0.18, 0.50, 17)

amp_grid = np.zeros((len(RHO_FINE2), len(K_FINE)))
cascade_grid = np.zeros_like(amp_grid)

total = len(K_FINE) * len(RHO_FINE2)
done = 0

for j, mk in enumerate(K_FINE):
    graphs = [make_er(N, mk) for _ in range(12)]
    for i, rho in enumerate(RHO_FINE2):
        amps = []
        cascades = []
        for G in graphs:
            for _ in range(8):
                cf, nf, amp = run_cascade(G, tau=TAU, rho=rho)
                amps.append(amp)
                cascades.append(cf)
        amp_grid[i, j] = np.mean(amps)
        cascade_grid[i, j] = np.mean(cascades)
        done += 1
        if done % 50 == 0:
            print(f"  {done}/{total}")

print(f"  {done}/{total} done.")

# Publication figure
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6.5))

extent = [K_FINE[0], K_FINE[-1], RHO_FINE2[0], RHO_FINE2[-1]]

# Left: amplification
amp_clipped = np.clip(amp_grid, 1.0, 50.0)
im1 = ax1.imshow(amp_clipped, aspect='auto', origin='lower', extent=extent,
                 norm=LogNorm(vmin=1.0, vmax=50.0),
                 cmap='PuBu', interpolation='bilinear')

try:
    cs1 = ax1.contour(K_FINE, RHO_FINE2, amp_grid,
                      levels=[1.5, 2.0, 5.0, 10.0, 20.0],
                      colors='black', linewidths=0.8, alpha=0.7)
    ax1.clabel(cs1, fmt='%.0f×', fontsize=9, inline=True)
except:
    pass

# Mark the analytic floor
ax1.axhline(y=1-np.sqrt(TAU), color=RED, linestyle='--', linewidth=1.5, alpha=0.8)
ax1.text(1.3, 1-np.sqrt(TAU)+0.008, r'$\rho_{\min}=1-\sqrt{\tau}$',
         fontsize=10, color=RED, alpha=0.8)

ax1.set_xlabel('Mean degree ⟨k⟩', fontsize=12)
ax1.set_ylabel(r'Contagion sensitivity $\rho$', fontsize=12)
ax1.set_title('Cascade Amplification', fontsize=13, fontweight='bold')
cb1 = fig.colorbar(im1, ax=ax1, shrink=0.85)
cb1.set_label('Amplification factor', fontsize=10)

# Right: cascade exposure
cas_clipped = np.clip(cascade_grid, 0.001, 0.5)
im2 = ax2.imshow(cas_clipped, aspect='auto', origin='lower', extent=extent,
                 norm=LogNorm(vmin=0.001, vmax=0.5),
                 cmap='YlOrRd', interpolation='bilinear')

try:
    cs2 = ax2.contour(K_FINE, RHO_FINE2, cascade_grid,
                      levels=[0.01, 0.03, 0.05, 0.10, 0.20],
                      colors='black', linewidths=0.8, alpha=0.7)
    ax2.clabel(cs2, fmt='%.0f%%',
               manual=False, fontsize=9, inline=True)
except:
    pass

ax2.axhline(y=1-np.sqrt(TAU), color='white', linestyle='--', linewidth=1.5, alpha=0.8)
ax2.text(1.3, 1-np.sqrt(TAU)+0.008, r'$\rho_{\min}=1-\sqrt{\tau}$',
         fontsize=10, color='white', alpha=0.9)

ax2.set_xlabel('Mean degree ⟨k⟩', fontsize=12)
ax2.set_ylabel(r'Contagion sensitivity $\rho$', fontsize=12)
ax2.set_title('Cascade Exposure', fontsize=13, fontweight='bold')
cb2 = fig.colorbar(im2, ax=ax2, shrink=0.85)
cb2.set_label('Fraction of pairs disrupted', fontsize=10)

fig.suptitle(f'Trust Cascade Phase Space — ER Benchmark\n'
             f'n={N}, τ={TAU}, with analytic floor '
             r'$\rho_{\min}=1-\sqrt{\tau}$',
             fontsize=14, y=1.02)

plt.tight_layout()
plt.savefig('/home/claude/publication_heatmap.png', dpi=150, bbox_inches='tight')
plt.close()
print("\nPublication heatmap saved.")


# ═══════════════════════════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)

print(f"\nProposition 1: ρ_min = 1 - √τ")
print(f"  At τ=0.55: analytic ρ_min = {1-np.sqrt(0.55):.4f}")
print(f"  Empirical confirmation: see plot")

print(f"\nB-Matched Topology Comparison:")
print(f"  At matched B, does modular still cascade differently from ER?")
for er_r, mod_r in zip(er_matched, mod_matched):
    if abs(er_r['actual_B'] - mod_r['actual_B']) < 1.0:
        er_cas_30 = [r['cascade'] for r in er_r['rho_results']
                     if abs(r['rho'] - 0.35) < 0.03]
        mod_cas_30 = [r['cascade'] for r in mod_r['rho_results']
                      if abs(r['rho'] - 0.35) < 0.03]
        if er_cas_30 and mod_cas_30:
            ratio = mod_cas_30[0] / max(er_cas_30[0], 0.001)
            print(f"  B≈{er_r['actual_B']:.1f}: ER cascade={er_cas_30[0]:.4f}  "
                  f"Mod cascade={mod_cas_30[0]:.4f}  "
                  f"ratio={ratio:.1f}×")

print(f"\nAll outputs saved.")
