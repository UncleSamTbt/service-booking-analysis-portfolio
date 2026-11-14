/* Pure calculations embedded in the dashboard and checked with Node. */
(function (scope) {
  'use strict';
  function filterBookings(records, filters) {
    return records.filter(row => Object.entries(filters).every(([key, value]) =>
      !value || (key === 'month' ? row.appointment_date.slice(0, 7) : row[key]) === value));
  }
  const mean = values => values.length ? values.reduce((a, b) => a + b, 0) / values.length : null;
  function computeMetrics(records) {
    const count = status => records.filter(row => row.status === status).length;
    const completed = records.filter(row => row.status === 'completed');
    const resolved = count('completed') + count('cancelled') + count('no_show');
    const scores = completed.map(row => row.satisfaction_score).filter(value => value !== null);
    return {
      booking_count: records.length, resolved_count: resolved,
      completed_count: count('completed'), cancelled_count: count('cancelled'),
      no_show_count: count('no_show'), scheduled_count: count('scheduled'),
      collected_revenue_cents: completed.reduce((total, row) => total + row.paid_amount_cents, 0),
      completion_rate_pct: resolved ? 100 * count('completed') / resolved : null,
      cancellation_rate_pct: resolved ? 100 * count('cancelled') / resolved : null,
      mean_lead_days: mean(records.map(row => row.lead_days)),
      feedback_response_count: scores.length, average_feedback_score: mean(scores),
      average_service_minutes: mean(completed.map(row => row.actual_minutes))
    };
  }
  scope.PortfolioMetrics = {filterBookings, computeMetrics};
})(globalThis);
