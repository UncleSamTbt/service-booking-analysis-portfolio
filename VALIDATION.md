# Validation record

Verified on **5 November 2026** using **Python 3.12.14** and **Node.js v24.22.1**. Python checks use the standard library; JavaScript checks use Node's built-in modules. All business records are synthetic.

## Implemented analysis

```text
python 04-data-analysis/pipeline.py
python -m unittest discover -s 04-data-analysis/tests -v
```

The pipeline validated **144 records** and rebuilt the analysis outputs and standalone dashboard. Collected revenue is **ZAR 51,015.00**, using the shared KPI definitions. The invented source contains 93 completed, 26 cancelled, 13 no-show and 12 scheduled bookings.

**15 Python tests passed.** Coverage includes a manually calculated fixture, invalid dates and controlled values, duplicate identifiers, payment/outcome constraints, fixed snapshot rules, cancellation reasons, missing feedback, empty selections, grouped-total reconciliation, output generation, full-input rejection and direct source-data totals.

The deterministic generator reproduced all 144 source rows and values exactly. The comparison normalised newline conventions because CSV writing and the publication text copy use different platform line endings.

## Implemented dashboard

```text
node 05-business-intelligence/test-dashboard.mjs
```

**Passed:** six Python baseline filter selections; a manually calculated fixture; empty and scheduled-only denominators; service-total reconciliation; source outcome counts; embedded source/data consistency; JavaScript syntax; and absence of external scripts, stylesheets or network-fetch dependencies.

The publication pass did not include manual browser interaction testing. Automated calculation and source checks do not establish browser accessibility or interaction coverage.

## Proposed operational work

The requirements, logical model, booking workflows, role controls, audit trail and **15 acceptance scenarios** are design artifacts. No operational booking application or production database is implemented. Every acceptance scenario is marked **specified, not run**. Passing analytics checks does not verify those operational controls.

## Publication review

- Reviewed **31 UTF-8 text files**, excluding caches, compiled files, source-control history and unrelated documents.
- Verified **15 local documentation links** and every acceptance-scenario reference in the traceability table.
- The excluded operational contract and earlier request-based test files are absent. Field mapping and traceability refer to workflows and plain record fields.
- Text scans found zero contact email addresses, phone-like numbers, private machine paths, known private organisation names, web addresses or common credential markers. Project descriptions contain neutral practice-project wording and identify the synthetic data and proposed work.
- Pattern checks supplement content review; they do not constitute a production security assessment.

Run the three commands above from the repository root to reproduce the implemented checks. Regenerate input with `python data/generate_synthetic_data.py`, then rerun the pipeline and checks.
