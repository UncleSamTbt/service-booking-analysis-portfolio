# KPI definitions and reconciliation rules

The same definitions are implemented in Python and JavaScript and checked against shared test cases. Every dashboard filter is applied **before** calculating these measures. Empty denominators return `null` and display as an em dash, rather than an invented zero-percent rate.

| Measure | Definition |
|---|---|
| Bookings | Count of selected booking rows; includes future scheduled bookings |
| Resolved bookings | Completed + cancelled + no-show booking counts |
| Completion rate | Completed / resolved bookings × 100 |
| Cancellation rate | Cancelled / resolved bookings × 100 |
| Collected revenue | Sum of `paid_amount_cents` for completed bookings only |
| Average lead time | Mean calendar days from creation to appointment, across all selected bookings |
| Average service duration | Mean `actual_minutes` for completed bookings |
| Feedback responses | Completed bookings with a recorded satisfaction score |
| Average feedback score | Mean recorded score, from 1 to 5; missing scores are excluded |

All amounts are integer cents until display. Rates are rounded to six decimals in saved analysis outputs; dashboard display uses one decimal place. A no-show is a separate outcome, not a cancellation. Each booking is one row. This is not a unique-customer count or a sales-funnel conversion rate.

Grouped CSVs include booking/outcome counts and collected revenue. Their booking counts and revenue must reconcile to the unfiltered totals. Dashboard baseline cases include the whole dataset, one service, one month, completed-only and scheduled-only selections.

The fixed reporting snapshot is 2026-03-31. The input validator rejects completed/cancelled/no-show outcomes after this date and scheduled bookings on or before it. This rule suits this snapshot exercise; a live operational system would need a more complete event history and explicit overdue-booking handling.
