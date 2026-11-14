# Project walkthrough

This practice project uses a fictional business and synthetic records. Chapters 01–03 specify proposed business and systems designs. Chapters 04–05 implement local data validation, analysis and reporting.

## Explore the project

1. Read the problem statement and acceptance criteria in chapter 01.
2. Trace R-03 through the field mapping, proposed payment workflow and acceptance scenarios in chapters 02–03.
3. Run the Python pipeline and inspect the input, validation report, grouped summaries and dashboard.
4. Explain why future scheduled bookings are excluded from completion and cancellation rates.
5. In a working copy, change one synthetic payment within its quote, rebuild and reconcile the revenue difference. Restore the input with the deterministic generator.
6. In a working copy, introduce a duplicate booking ID and confirm that validation rejects the entire input.
7. Filter the dashboard by service and month, then reconcile booking counts and collected revenue to the source records.

## Interpretation and extensions

Quoted value differs from collected revenue; service duration differs from staff utilisation; missing feedback differs from a score of zero. Synthetic differences between services or channels do not establish business causes.

The proposed operational workflows require stakeholder validation and implementation before their acceptance scenarios can be executed. Potential extensions include scheduling timestamps, audited corrections and payment transaction history. The existing local dashboard uses HTML and JavaScript; this project does not include SQL or a Power BI report.
