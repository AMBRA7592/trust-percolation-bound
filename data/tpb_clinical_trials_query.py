"""
Trust Percolation Bound — Clinical Trial Network Analysis
Run in Google Colab.

Queries ClinicalTrials.gov API v2 for Phase III oncology trials (2022-2025),
extracts investigators and sites, computes cross-sponsor overlap.
"""

import requests
import time
from collections import defaultdict, Counter

# ─── Step 1: Test the API ───────────────────────────────────

print("Testing API connection...")
test = requests.get(
    "https://clinicaltrials.gov/api/v2/studies",
    params={
        "query.cond": "breast cancer",
        "pageSize": 1,
        "countTotal": "true",
        "format": "json",
    }
)
print(f"  Status: {test.status_code}")
if test.status_code == 200:
    print(f"  Total breast cancer studies: {test.json().get('totalCount', '?')}")
    print("  API working.\n")
else:
    print(f"  Error: {test.text[:300]}")
    raise SystemExit("API failed")


# ─── Step 2: Fetch Phase III cancer trials ──────────────────

BASE_URL = "https://clinicaltrials.gov/api/v2/studies"

def fetch_studies():
    """Fetch Phase III interventional cancer trials, 2022+."""
    studies = []
    next_token = None
    page = 0

    while True:
        params = {
            "query.cond": "cancer",
            # Use query.term with AREA syntax for phase + type + date
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
            print(f"  Error {resp.status_code}: {resp.text[:300]}")
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
print("FETCHING PHASE III ONCOLOGY TRIALS (2022+)")
print("=" * 60)
studies = fetch_studies()
print(f"\nFetched: {len(studies)}")


# ─── Step 3: Extract data ──────────────────────────────────

def dg(d, *keys):
    for k in keys:
        if isinstance(d, dict):
            d = d.get(k)
        elif isinstance(d, list) and isinstance(k, int) and k < len(d):
            d = d[k]
        else:
            return None
    return d


sponsor_trials = defaultdict(set)
inv_sponsors = defaultdict(set)
inv_trials = defaultdict(set)
site_sponsors = defaultdict(set)
site_trials = defaultdict(set)
n_inv = 0
n_sites = 0

for s in studies:
    p = s.get("protocolSection", {})
    nct = dg(p, "identificationModule", "nctId") or "?"
    sponsor = dg(p, "sponsorCollaboratorsModule", "leadSponsor", "name") or "?"
    sponsor_trials[sponsor].add(nct)

    officials = dg(p, "contactsLocationsModule", "overallOfficials") or []
    if officials:
        n_inv += 1
    for o in officials:
        nm = (o.get("name") or "").strip().lower()
        if nm:
            inv_sponsors[nm].add(sponsor)
            inv_trials[nm].add(nct)

    locs = dg(p, "contactsLocationsModule", "locations") or []
    if locs:
        n_sites += 1
    for l in locs:
        fac = (l.get("facility") or "").strip().lower()
        city = (l.get("city") or "").strip().lower()
        ctry = (l.get("country") or "").strip().lower()
        if fac:
            k = f"{fac}|{city}|{ctry}"
            site_sponsors[k].add(sponsor)
            site_trials[k].add(nct)


total = max(len(studies), 1)
print(f"\n{'='*60}\nEXTRACTION\n{'='*60}")
print(f"Trials: {len(studies)}")
print(f"Sponsors: {len(sponsor_trials)}")
print(f"Trials w/ investigators: {n_inv}")
print(f"Trials w/ sites: {n_sites}")
print(f"Unique investigators: {len(inv_sponsors)}")
print(f"Unique sites: {len(site_sponsors)}")


# ─── Step 4: Investigator overlap ────────────────────────────

inv_m = {n: s for n, s in inv_sponsors.items() if len(s) >= 2}
ti = max(len(inv_sponsors), 1)

print(f"\n{'='*60}\nINVESTIGATOR OVERLAP\n{'='*60}")
print(f"≥2 sponsors: {len(inv_m)}/{ti} ({100*len(inv_m)/ti:.1f}%)")

cd = Counter(len(s) for s in inv_sponsors.values())
print("\nDistribution:")
for ns in sorted(cd.keys(), reverse=True)[:8]:
    print(f"  {ns} sponsors: {cd[ns]} investigators")

print("\nTop 15:")
for nm, sp in sorted(inv_m.items(), key=lambda x: len(x[1]), reverse=True)[:15]:
    print(f"  {nm[:55]:55s} {len(sp):2d} sp  {len(inv_trials[nm]):2d} tr")


# ─── Step 5: Site overlap ───────────────────────────────────

site_m = {s: sp for s, sp in site_sponsors.items() if len(sp) >= 2}
ts = max(len(site_sponsors), 1)

print(f"\n{'='*60}\nSITE OVERLAP\n{'='*60}")
print(f"≥2 sponsors: {len(site_m)}/{ts} ({100*len(site_m)/ts:.1f}%)")

cds = Counter(len(s) for s in site_sponsors.values())
print("\nDistribution:")
for ns in sorted(cds.keys(), reverse=True)[:8]:
    print(f"  {ns} sponsors: {cds[ns]} sites")

print("\nTop 15:")
for k, sp in sorted(site_m.items(), key=lambda x: len(x[1]), reverse=True)[:15]:
    print(f"  {k.split('|')[0][:55]:55s} {len(sp):2d} sp  {len(site_trials[k]):2d} tr")


# ─── Step 6: Sponsor concentration ──────────────────────────

ss = sorted([(s, len(t)) for s, t in sponsor_trials.items()],
            key=lambda x: x[1], reverse=True)

print(f"\n{'='*60}\nSPONSOR CONCENTRATION\n{'='*60}")
cum = 0
for s, c in ss[:20]:
    cum += c
    print(f"  {s[:55]:55s} {c:4d}  ({100*c/total:5.1f}%  cum {100*cum/total:5.1f}%)")


# ─── Step 7: Summary ────────────────────────────────────────

print(f"\n{'='*60}\nSUMMARY FOR §8.2\n{'='*60}")
if ss:
    t5 = sum(c for _, c in ss[:5])
    t10 = sum(c for _, c in ss[:10])
    print(f"""
Trials: {len(studies)}
Sponsors: {len(sponsor_trials)}
Top sponsor: {ss[0][0]} ({ss[0][1]} trials, {100*ss[0][1]/total:.1f}%)
Top 5: {t5} ({100*t5/total:.1f}%)  Top 10: {t10} ({100*t10/total:.1f}%)
Investigators: {len(inv_sponsors)}  (≥2 sponsors: {len(inv_m)}, {100*len(inv_m)/ti:.1f}%)
Sites: {len(site_sponsors)}  (≥2 sponsors: {len(site_m)}, {100*len(site_m)/ts:.1f}%)
""")
print("Done.")
