# 04 · Data Analyst — reproducible validation and analysis

**Implemented with Python's standard library. All records are synthetic.**

From the repository root, run `python 04-data-analysis/pipeline.py`. The validator checks all 16 raw fields, identifiers, calendar dates, controlled values, integer cents, payment limits and conditional outcome fields. Any invalid record rejects the full input before analysis outputs are written; no rows are silently dropped.

## Outputs

| File in `outputs/` | Purpose |
|---|---|
| `clean_bookings.csv` | Validated typed records with derived calendar `lead_days` |
| `kpis.csv` | Whole-dataset metrics using the shared definitions |
| `monthly_summary.csv` | Appointment-month counts, outcomes and collected revenue |
| `service_summary.csv` | The same metrics grouped by service |
| `channel_summary.csv` | The same metrics grouped by request channel |
| `validation_report.json` | Row count, reporting date, checks and rejection policy |

The default build also embeds the validated rows into the standalone dashboard and writes its six checked baseline cases. Use `--skip-dashboard` when working on analysis alone.

## Verification

Run `python -m unittest discover -s 04-data-analysis/tests -v` from the root. Tests use a manually calculated five-row fixture, invalid-record cases, snapshot/date boundaries, empty selections and independent grouped-total reconciliation. They also compare the actual synthetic dataset with its documented 144-row outcome counts and direct CSV revenue sum.

The report describes this artificial dataset only. Differences between services or channels do not establish causes or predict a real company's performance.
