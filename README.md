# Service-booking analysis portfolio

**Fictional business · synthetic data · analyst practice project**

This portfolio connects five analyst roles through a fictional home-services business, **Demo Service Co.**, with a booking process and consistent reporting needs. The business, customers, identifiers and transactions are invented. It combines proposed business and systems designs with an implemented Python analysis pipeline and an interactive HTML dashboard.

| Role | Project | Artifacts |
|---|---|---|
| Business Analyst | [01 — Business analysis](01-business-analysis/README.md) | Problem framing, process diagrams, requirements, user stories and acceptance criteria |
| Business Systems Analyst | [02 — Business systems analysis](02-business-systems-analysis/README.md) | Logical data model, field mapping, data dictionary and requirements traceability |
| Systems Analyst | [03 — Systems analysis](03-systems-analysis/README.md) | Proposed workflows, status transitions, exception handling and acceptance scenarios |
| Data Analyst | [04 — Data analysis](04-data-analysis/README.md) | Executable Python validation and analysis pipeline, CSV outputs and unit tests |
| Business Intelligence Analyst | [05 — Business intelligence](05-business-intelligence/README.md) | Standalone interactive HTML dashboard, shared KPI definitions and calculation checks |

## Run the implemented parts

Requires Python 3.10+; no third-party Python packages are needed. Node.js 18+ is optional for the dashboard calculation checks. Run from this repository's root:

```text
python 04-data-analysis/pipeline.py
python -m unittest discover -s 04-data-analysis/tests -v
node 05-business-intelligence/test-dashboard.mjs
```

Open [the dashboard](05-business-intelligence/dashboard.html) directly in a browser. It contains its own data, styles and calculation code. Filters and CSV export work locally, with no web server, account or external service.

To regenerate the deterministic synthetic input:

```text
python data/generate_synthetic_data.py
python 04-data-analysis/pipeline.py
```

For another input using the same schema:

```text
python 04-data-analysis/pipeline.py --input path/to/bookings.csv --output-dir path/to/results --skip-dashboard
```

The pipeline validates the entire input before writing results.

## Project scope

- Chapters 01–03 contain **proposed designs and specified acceptance scenarios**. The operational booking application, database, access controls and audit trail have not been implemented or tested.
- The Python analysis and browser dashboard **are implemented**. Automated checks validate input rules, calculations and consistency with a checked baseline.
- The fixed reporting snapshot is **31 March 2026**. Scheduled bookings fall after that date. All amounts use South African rand, stored as integer cents.
- Collected revenue means payments recorded for completed bookings. It is not quoted value, profit or accounting revenue recognition.
- The synthetic records cannot establish causes, operational capacity or real-world commercial performance. No real business improvement is claimed.

See the [project walkthrough](LEARNING_GUIDE.md), [KPI definitions](KPI_DEFINITIONS.md) and [validation record](VALIDATION.md).
