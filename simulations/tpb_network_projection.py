"""
Trust Percolation Bound — Network Projection Statistics
Run in Google Colab after installing: pip install networkx numpy

Queries ClinicalTrials.gov API v2 for Phase III oncology trials,
builds the sponsor-sponsor one-mode projection (two sponsors connected
if they share at least one trial site), and computes:
  - Clustering coefficient
  - Mean degree
  - Molloy-Reed branching factor B
  - Degree distribution summary

These are proxy statistics for the trust-intermediation graph G_I.
"""

import requests
import time
import numpy as np
import networkx as nx
from collections import defaultdict

# ─── Step 1: Fetch trials (same query as before) ────────────

BASE_URL = "https://clinicaltrials.gov/api/v2/studies"

def fetch_studies():
    studies = []
    next_token = None
    page = 0
    while True:
        params = {
            "query.cond": "cancer",
            "query.term": (
                "AREA[Phase](PHASE3) "
                "AND AREA[StudyType](INTERVENTIONAL) "
                "AND AREA[StartDate]RANGE[2022-01-01, MAX]"
            ),
            "pageSize": 1000,
            "format": "json",
        }
        if page == 0:
            params["countTotal"] = "true"
        if next_token:
            params["pageToken"] = next_token
        resp = requests.get(BASE_URL, params=params)
        if resp.status_code != 200:
            print(f"  Error {resp.status_code}: {resp.text[:200]}")
            break
        data = resp.json()
        if page == 0:
            print(f"  Total matching: {data.get('totalCount', '?')}")
        batch = data.get("studies", [])
        studies.extend(batch)
        page += 1
        print(f"  Page {page}: {len(batch)} (total: {len(studies)})")
        next_token = data.get("nextPageToken")
        if not next_token or len(batch) == 0:
            break
        time.sleep(0.5)
    return studies

print("=" * 60)
print("FETCHING PHASE III ONCOLOGY TRIALS")
print("=" * 60)
studies = fetch_studies()
print(f"Fetched: {len(studies)}")


# ─── Step 2: Build site-sponsor bipartite mappings ──────────

def dg(d, *keys):
    for k in keys:
        if isinstance(d, dict):
            d = d.get(k)
        elif isinstance(d, list) and isinstance(k, int) and k < len(d):
            d = d[k]
        else:
            return None
    return d

site_to_sponsors = defaultdict(set)
sponsor_to_sites = defaultdict(set)

for s in studies:
    p = s.get("protocolSection", {})
    sponsor = dg(p, "sponsorCollaboratorsModule", "leadSponsor", "name") or "?"
    locs = dg(p, "contactsLocationsModule", "locations") or []
    for loc in locs:
        fac = (loc.get("facility") or "").strip().lower()
        city = (loc.get("city") or "").strip().lower()
        ctry = (loc.get("country") or "").strip().lower()
        if fac:
            site_key = f"{fac}|{city}|{ctry}"
            site_to_sponsors[site_key].add(sponsor)
            sponsor_to_sites[sponsor].add(site_key)

print(f"\nSites: {len(site_to_sponsors)}")
print(f"Sponsors: {len(sponsor_to_sites)}")


# ─── Step 3: Build sponsor-sponsor projection ──────────────
# Two sponsors are connected if they share at least one trial site.
# Edge weight = number of shared sites.

print("\n" + "=" * 60)
print("BUILDING SPONSOR-SPONSOR PROJECTION")
print("(Two sponsors linked if they share ≥1 trial site)")
print("=" * 60)

G = nx.Graph()
G.add_nodes_from(sponsor_to_sites.keys())

# For each site with ≥2 sponsors, add edges between all sponsor pairs
n_multi_sites = 0
for site, sponsors in site_to_sponsors.items():
    if len(sponsors) >= 2:
        n_multi_sites += 1
        sponsor_list = sorted(sponsors)
        for i in range(len(sponsor_list)):
            for j in range(i + 1, len(sponsor_list)):
                if G.has_edge(sponsor_list[i], sponsor_list[j]):
                    G[sponsor_list[i]][sponsor_list[j]]['weight'] += 1
                else:
                    G.add_edge(sponsor_list[i], sponsor_list[j], weight=1)

print(f"Multi-sponsor sites (projection sources): {n_multi_sites}")
print(f"Sponsor nodes: {G.number_of_nodes()}")
print(f"Sponsor-sponsor edges: {G.number_of_edges()}")


# ─── Step 4: Compute network statistics ─────────────────────

print("\n" + "=" * 60)
print("NETWORK STATISTICS (SPONSOR-SPONSOR PROJECTION)")
print("=" * 60)

# Remove isolates for meaningful statistics
isolates = list(nx.isolates(G))
G_connected = G.copy()
G_connected.remove_nodes_from(isolates)

n_nodes = G_connected.number_of_nodes()
n_edges = G_connected.number_of_edges()

print(f"\nConnected sponsors (non-isolates): {n_nodes}")
print(f"Edges: {n_edges}")
print(f"Isolated sponsors (no shared sites): {len(isolates)}")

if n_nodes > 0:
    # Degree distribution
    degrees = np.array([d for _, d in G_connected.degree()])
    mean_k = degrees.mean()
    mean_k2 = np.mean(degrees ** 2)

    # Molloy-Reed branching factor
    B = (mean_k2 - mean_k) / mean_k if mean_k > 0 else 0

    # Clustering coefficient
    cc = nx.average_clustering(G_connected)

    # Transitivity (global clustering)
    transitivity = nx.transitivity(G_connected)

    # Giant component
    gcc = max(nx.connected_components(G_connected), key=len)
    gcc_frac = len(gcc) / n_nodes

    print(f"\nMean degree <k>: {mean_k:.2f}")
    print(f"Mean <k^2>: {mean_k2:.1f}")
    print(f"Molloy-Reed branching factor B: {B:.2f}")
    print(f"Average clustering coefficient: {cc:.4f}")
    print(f"Global transitivity: {transitivity:.4f}")
    print(f"Giant component: {len(gcc)} nodes ({100*gcc_frac:.1f}% of connected sponsors)")

    print(f"\nDegree distribution:")
    print(f"  Min: {degrees.min()}")
    print(f"  Median: {np.median(degrees):.0f}")
    print(f"  Mean: {mean_k:.1f}")
    print(f"  Max: {degrees.max()}")
    print(f"  Std: {degrees.std():.1f}")

    # Top-degree sponsors
    print(f"\nTop 10 sponsors by degree (shared-site connections):")
    top = sorted(G_connected.degree(), key=lambda x: x[1], reverse=True)[:10]
    for sponsor, deg in top:
        print(f"  {sponsor[:55]:55s} degree={deg}")


    # ─── Step 5: Summary for §8.2 ──────────────────────────

    print(f"\n{'='*60}")
    print("NUMBERS FOR §8.2")
    print(f"{'='*60}")
    print(f"""
SPONSOR-SPONSOR PROJECTION (via shared trial sites):
  Sponsors (non-isolated): {n_nodes}
  Edges: {n_edges}
  Mean degree: {mean_k:.1f}
  Molloy-Reed B: {B:.1f}
  Average clustering coefficient: {cc:.3f}
  Global transitivity: {transitivity:.3f}
  Giant component: {len(gcc)} ({100*gcc_frac:.1f}%)

Interpretation:
  - Clustering coefficient of {cc:.3f} is {"HIGH" if cc > 0.3 else "MODERATE" if cc > 0.1 else "LOW"}
    (for comparison: ER at same <k> would have C ≈ {mean_k/n_nodes:.4f})
  - B = {B:.1f} {">> 1: well above percolation threshold" if B > 1 else "≈ 1: near percolation threshold" if B > 0.8 else "< 1: below percolation threshold"}
  - Giant component at {100*gcc_frac:.1f}% confirms the network is well-connected
""")

    # ─── Step 6: Also do investigator-sponsor projection ────

    print("=" * 60)
    print("INVESTIGATOR-SPONSOR PROJECTION (bonus)")
    print("=" * 60)

    inv_to_sponsors = defaultdict(set)
    for s in studies:
        p = s.get("protocolSection", {})
        sponsor = dg(p, "sponsorCollaboratorsModule", "leadSponsor", "name") or "?"
        officials = dg(p, "contactsLocationsModule", "overallOfficials") or []
        for o in officials:
            nm = (o.get("name") or "").strip().lower()
            if nm and nm not in ["study director", "medical director",
                                  "clinical trials", "medical monitor"]:
                inv_to_sponsors[nm].add(sponsor)

    G2 = nx.Graph()
    for inv, sponsors in inv_to_sponsors.items():
        if len(sponsors) >= 2:
            sponsor_list = sorted(sponsors)
            for i in range(len(sponsor_list)):
                for j in range(i + 1, len(sponsor_list)):
                    if not G2.has_edge(sponsor_list[i], sponsor_list[j]):
                        G2.add_edge(sponsor_list[i], sponsor_list[j])

    if G2.number_of_nodes() > 0:
        cc2 = nx.average_clustering(G2)
        degs2 = np.array([d for _, d in G2.degree()])
        print(f"  Nodes: {G2.number_of_nodes()}")
        print(f"  Edges: {G2.number_of_edges()}")
        print(f"  Mean degree: {degs2.mean():.1f}")
        print(f"  Clustering: {cc2:.3f}")
    else:
        print("  No multi-sponsor investigators (excluding placeholders)")

else:
    print("No connected sponsors found.")

print("\nDone.")
