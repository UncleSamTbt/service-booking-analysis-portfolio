# Synthetic source data

`bookings.csv` contains **144 invented records**, generated deterministically with seed `20260331`. It contains no real business, customer, technician or contact information. The names “Demo North”, “Demo Central” and “Demo South” are fictional location labels.

The reporting snapshot is 31 March 2026: 132 resolved bookings (93 completed, 26 cancelled, 13 no-show) and 12 scheduled April bookings. Amounts are ZAR cents. Feedback is intentionally missing for some completed bookings to demonstrate correct handling of missing values.

Regenerate with `python data/generate_synthetic_data.py`, then rerun the pipeline. This is a reproducible learning dataset, not a sample from an actual company and not evidence of real business performance. See the data dictionary in chapter 02.
