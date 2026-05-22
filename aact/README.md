# AACT Investigator-Overlap Analysis

This directory contains the SQL query, snapshot manifest, and result CSVs
underlying the investigator-overlap analysis in §8.2 of Brandes (2026),
*The Trust Percolation Bound*.

## What this reproduces

The paper reports that, among Phase III interventional cancer trials starting
2018 or later, ~12% of named investigators serve as PI on trials for two or
more distinct lead pharmaceutical sponsors, with the most cross-sponsor
investigators spanning 8 lead sponsors. This is offered as evidence that the
trust-intermediation graph of the global clinical trial system exhibits
persistent local overlap consistent with the cascade theory's clustering
prerequisite.

## How to reproduce

You need a free AACT account (https://aact.ctti-clinicaltrials.org/users/sign_up)
and a PostgreSQL client (psql, pgAdmin, DBeaver, any will work).

With psql:

    psql "host=aact-db.ctti-clinicaltrials.org port=5432 dbname=aact user=YOUR_USERNAME sslmode=require" -f aact_investigator_overlap.sql

You will be prompted for your AACT password. Runtime: ~30–60 seconds.
Three CSVs are written to the current directory:

- headline_metrics.csv — total / multi-sponsor counts, percentage, sponsor and trial counts
- top20_cross_sponsor_investigators.csv — the 20 investigators with the most lead-sponsor diversity
- sponsors_per_investigator_distribution.csv — full distribution of n_sponsors per investigator

## Snapshot

snapshot_manifest.json records the exact query parameters, the AACT server
version, the run date, and the resulting counts for the snapshot underlying
the paper's reported numbers. AACT is updated daily from ClinicalTrials.gov;
re-running on a later date will produce slightly different counts as new
trials accrue. The qualitative findings (heavy-tailed distribution, ~12%
cross-sponsor fraction, max-span ≥ 7 sponsors) are robust to date drift.

## Identity caveat

Investigators are identified by raw facility_investigators.name strings,
trimmed but not otherwise normalized. The same physical person appearing
with different name spellings (e.g. with vs. without middle initial) is
counted as distinct investigators. This biases the multi-sponsor fraction
downward: the reported 11.76% is a lower bound on the true cross-sponsor
overlap. Name-normalization would only increase the reported fraction.

## Citation

If you use this data or query, please cite:

> Brandes, A. (2026). The Trust Percolation Bound: Correlated Trust Failure
> and the Structural Limits of Trust Governance. arXiv:XXXX.XXXXX

and AACT itself:

> Aggregate Analysis of ClinicalTrials.gov (AACT) Database. Clinical Trials
> Transformation Initiative (CTTI). Available at: https://aact.ctti-clinicaltrials.org/
> (Accessed: 2026-05-22).
