-- ============================================================
-- Trust Percolation Bound — AACT Investigator-Overlap Query
-- Reproduces the investigator-level overlap statistics in §8.2
-- of Brandes (2026), "The Trust Percolation Bound".
--
-- Universe: Phase III interventional cancer trials, start date >= 2018-01-01
-- Identity: ctgov.facility_investigators.name (free-text, no normalization)
-- Sponsor:  ctgov.sponsors WHERE lead_or_collaborator = 'lead'
-- ============================================================

\timing on
\pset footer off

-- ---- Q1: Universe -------------------------------------------
DROP TABLE IF EXISTS tpb_trials_universe;
CREATE TEMP TABLE tpb_trials_universe AS
SELECT DISTINCT s.nct_id, s.start_date
FROM ctgov.studies s
JOIN ctgov.conditions c ON c.nct_id = s.nct_id
WHERE s.phase = 'PHASE3'
  AND s.study_type = 'INTERVENTIONAL'
  AND s.start_date >= DATE '2018-01-01'
  AND (
        c.downcase_name LIKE '%cancer%'
     OR c.downcase_name LIKE '%carcinoma%'
     OR c.downcase_name LIKE '%neoplasm%'
     OR c.downcase_name LIKE '%tumor%'
     OR c.downcase_name LIKE '%tumour%'
     OR c.downcase_name LIKE '%leukemia%'
     OR c.downcase_name LIKE '%leukaemia%'
     OR c.downcase_name LIKE '%lymphoma%'
     OR c.downcase_name LIKE '%melanoma%'
     OR c.downcase_name LIKE '%sarcoma%'
     OR c.downcase_name LIKE '%myeloma%'
     OR c.downcase_name LIKE '%glioma%'
     OR c.downcase_name LIKE '%glioblastoma%'
      );

SELECT 'trials_in_universe' AS metric, COUNT(*) AS value FROM tpb_trials_universe;

-- ---- Q2: Investigator -> Lead Sponsor mapping ---------------
DROP TABLE IF EXISTS tpb_inv_sponsor;
CREATE TEMP TABLE tpb_inv_sponsor AS
SELECT DISTINCT
    TRIM(fi.name)  AS investigator_name,
    TRIM(sp.name)  AS sponsor_name,
    t.nct_id
FROM tpb_trials_universe t
JOIN ctgov.facilities f             ON f.nct_id      = t.nct_id
JOIN ctgov.facility_investigators fi ON fi.facility_id = f.id
JOIN ctgov.sponsors sp              ON sp.nct_id     = t.nct_id
WHERE sp.lead_or_collaborator = 'lead'
  AND fi.name IS NOT NULL
  AND TRIM(fi.name) <> ''
  AND LOWER(TRIM(fi.name)) NOT IN (
        'study director',
        'principal investigator',
        'sub-investigator',
        'subinvestigator',
        'sub investigator',
        'study chair',
        'study principal investigator',
        'investigator'
  );

-- ---- Q3a: Headline metrics ----------------------------------
\copy (SELECT 'total_named_investigators' AS metric, COUNT(DISTINCT investigator_name)::text AS value FROM tpb_inv_sponsor UNION ALL SELECT 'multi_sponsor_investigators', COUNT(*)::text FROM (SELECT investigator_name FROM tpb_inv_sponsor GROUP BY investigator_name HAVING COUNT(DISTINCT sponsor_name) >= 2) x UNION ALL SELECT 'pct_multi_sponsor', ROUND(100.0 * (SELECT COUNT(*) FROM (SELECT investigator_name FROM tpb_inv_sponsor GROUP BY investigator_name HAVING COUNT(DISTINCT sponsor_name) >= 2) x) / NULLIF((SELECT COUNT(DISTINCT investigator_name) FROM tpb_inv_sponsor),0), 2)::text UNION ALL SELECT 'distinct_lead_sponsors', COUNT(DISTINCT sponsor_name)::text FROM tpb_inv_sponsor UNION ALL SELECT 'distinct_trials_w_named_inv', COUNT(DISTINCT nct_id)::text FROM tpb_inv_sponsor) TO 'headline_metrics.csv' WITH (FORMAT CSV, HEADER);

-- ---- Q3b: Top 20 most cross-sponsor investigators -----------
\copy (SELECT investigator_name, COUNT(DISTINCT sponsor_name) AS n_sponsors, COUNT(DISTINCT nct_id) AS n_trials FROM tpb_inv_sponsor GROUP BY investigator_name ORDER BY n_sponsors DESC, n_trials DESC LIMIT 20) TO 'top20_cross_sponsor_investigators.csv' WITH (FORMAT CSV, HEADER);

-- ---- Q3c: Full distribution of sponsors-per-investigator ----
\copy (SELECT n_sponsors, COUNT(*) AS n_investigators FROM (SELECT investigator_name, COUNT(DISTINCT sponsor_name) AS n_sponsors FROM tpb_inv_sponsor GROUP BY investigator_name) x GROUP BY n_sponsors ORDER BY n_sponsors) TO 'sponsors_per_investigator_distribution.csv' WITH (FORMAT CSV, HEADER);

\echo ''
\echo '=== Done. Three CSVs written to current directory. ==='
