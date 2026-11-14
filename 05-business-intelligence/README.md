# 05 · Business Intelligence Analyst — interactive reporting

**Implemented HTML/JavaScript dashboard. Fictional business, synthetic data, no external services.**

Open `dashboard.html` in a browser. It includes all styles, data and calculation code in one file, so it works without installation or a local server. Filter by service, outcome, request channel and appointment month; reset the selection or download the selected records as CSV.

The cards, outcome breakdown, service comparison, monthly table and record preview all use the same filtered rows. Completion and cancellation percentages use resolved bookings only. Missing feedback is excluded and its response count is displayed. Currency is shown as ZAR but stored/calculated as integer cents.

`dashboard.template.html` and `dashboard_metrics.js` are editable sources. Running the Python pipeline regenerates `dashboard.html` and `metrics-baseline.json` from the validated CSV. Do not edit embedded generated data manually.

Optional JavaScript checks: `node 05-business-intelligence/test-dashboard.mjs`. These use Node's built-in modules and compare six filter selections to Python's baseline, plus a hand-calculated fixture and empty/scheduled denominator cases. They also confirm that the generated HTML embeds the tested source and has no external script, stylesheet or fetch dependency.

This is a custom HTML/JavaScript dashboard. KPI definitions and calculation checks are included in this project.
