"""
Trust Percolation Bound — Projection Threshold Robustness
Run in Google Colab after the main tpb_network_projection.py script.

Tests how sponsor-sponsor projection statistics change when we require
≥2, ≥3, or ≥5 shared sites before adding a projection edge.
This addresses the bipartite projection inflation concern:
single-site overlaps may be incidental, while multi-site overlaps
represent genuine shared infrastructure.

Paste this into a new Colab cell after the main projection script
has already run (it reuses the site_to_sponsors and sponsor_to_sites
dictionaries from that script).
"""

import numpy as np
import networkx as nx
from collections import defaultdict

# If running standalone, you need to re-fetch data first.
# If running after the main script, site_to_sponsors and sponsor_to_sites
# are already in memory.

THRESHOLDS = [1, 2, 3, 5]

print("=" * 70)
print("PROJECTION THRESHOLD ROBUSTNESS ANALYSIS")
print("Edge included only if sponsors share ≥ w trial sites")
print("=" * 70)

results = []

for w in THRESHOLDS:
    G = nx.Graph()
    G.add_nodes_from(sponsor_to_sites.keys())

    # Build projection with weight threshold
    # First compute all pairwise weights
    pair_weights = defaultdict(int)
    for site, sponsors in site_to_sponsors.items():
        if len(sponsors) >= 2:
            sponsor_list = sorted(sponsors)
            for i in range(len(sponsor_list)):
                for j in range(i + 1, len(sponsor_list)):
                    pair_weights[(sponsor_list[i], sponsor_list[j])] += 1

    # Add edges only if weight >= threshold
    for (s1, s2), weight in pair_weights.items():
        if weight >= w:
            G.add_edge(s1, s2, weight=weight)

    # Remove isolates
    isolates = list(nx.isolates(G))
    G_conn = G.copy()
    G_conn.remove_nodes_from(isolates)

    n_nodes = G_conn.number_of_nodes()
    n_edges = G_conn.number_of_edges()

    if n_nodes > 0:
        degrees = np.array([d for _, d in G_conn.degree()])
        mean_k = degrees.mean()
        mean_k2 = np.mean(degrees ** 2)
        B = (mean_k2 - mean_k) / mean_k if mean_k > 0 else 0
        cc = nx.average_clustering(G_conn)
        transitivity = nx.transitivity(G_conn)

        # Giant component
        gcc = max(nx.connected_components(G_conn), key=len)
        gcc_frac = len(gcc) / n_nodes

        row = {
            'threshold': w,
            'nodes': n_nodes,
            'edges': n_edges,
            'mean_k': mean_k,
            'B': B,
            'C_avg': cc,
            'C_trans': transitivity,
            'gcc_frac': gcc_frac,
        }
        results.append(row)

        print(f"\n--- Threshold w ≥ {w} shared sites ---")
        print(f"  Connected sponsors: {n_nodes}")
        print(f"  Edges: {n_edges}")
        print(f"  Mean degree: {mean_k:.1f}")
        print(f"  Molloy-Reed B: {B:.1f}")
        print(f"  Avg clustering: {cc:.3f}")
        print(f"  Transitivity: {transitivity:.3f}")
        print(f"  Giant component: {len(gcc)} ({100*gcc_frac:.1f}%)")
    else:
        print(f"\n--- Threshold w ≥ {w}: no connected sponsors ---")

print("\n" + "=" * 70)
print("SUMMARY TABLE FOR §8.2")
print("=" * 70)
print(f"\n{'w':>3s}  {'Nodes':>6s}  {'Edges':>6s}  {'<k>':>6s}  {'B':>7s}  {'C_avg':>6s}  {'C_trans':>7s}  {'GCC%':>6s}")
print("-" * 60)
for r in results:
    print(f"{r['threshold']:>3d}  {r['nodes']:>6d}  {r['edges']:>6d}  {r['mean_k']:>6.1f}  {r['B']:>7.1f}  {r['C_avg']:>6.3f}  {r['C_trans']:>7.3f}  {100*r['gcc_frac']:>5.1f}%")

print(f"""
INTERPRETATION:
If clustering drops sharply at w≥2 or w≥3, the w=1 clustering is largely
a projection artifact. If it remains high, the clustering reflects genuine
multi-site shared infrastructure, not incidental single-site overlaps.

Key comparison:
  ER baseline at matched <k> for w=1: C_ER ≈ {results[0]['mean_k']/results[0]['nodes']:.4f}
""")
