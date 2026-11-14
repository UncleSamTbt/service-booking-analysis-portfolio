"""Meaningful arithmetic, validation and reconciliation checks; no dependencies."""
import csv
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

MODULE_PATH = Path(__file__).resolve().parents[1] / "pipeline.py"
SPEC = importlib.util.spec_from_file_location("portfolio_pipeline", MODULE_PATH)
pipeline = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(pipeline)


def fixture():
    base = {
        "booking_id": "B0001", "customer_id": "C001", "created_date": "2026-01-01",
        "appointment_date": "2026-01-03", "service_code": "CLEAN", "customer_segment": "household",
        "channel": "web", "suburb": "Demo North", "technician_id": "T01", "status": "completed",
        "quoted_amount_cents": "10000", "paid_amount_cents": "10000", "scheduled_minutes": "30",
        "actual_minutes": "30", "satisfaction_score": "4", "cancellation_reason": "",
    }
    rows = [dict(base)]
    rows.append(dict(base, booking_id="B0002", appointment_date="2026-01-05", service_code="REPAIR", quoted_amount_cents="5000", paid_amount_cents="5000", actual_minutes="60", satisfaction_score="5"))
    rows.append(dict(base, booking_id="B0003", created_date="2026-01-02", appointment_date="2026-01-05", status="cancelled", paid_amount_cents="0", actual_minutes="", satisfaction_score="", cancellation_reason="Customer unavailable"))
    rows.append(dict(base, booking_id="B0004", appointment_date="2026-01-08", status="no_show", paid_amount_cents="0", actual_minutes="", satisfaction_score=""))
    rows.append(dict(base, booking_id="B0005", created_date="2026-03-30", appointment_date="2026-04-01", status="scheduled", paid_amount_cents="0", actual_minutes="", satisfaction_score=""))
    return rows


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "input.csv"

    def write(self, rows):
        with self.path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=pipeline.FIELDS)
            writer.writeheader()
            writer.writerows(rows)
        return self.path

    def read(self, rows=None):
        return pipeline.read_data(self.write(fixture() if rows is None else rows))

    def assert_invalid(self, **changes):
        rows = fixture()
        rows[0].update(changes)
        with self.assertRaises(ValueError):
            self.read(rows)

    def test_fixture_metrics(self):
        metrics = pipeline.calculate_metrics(self.read())
        expected = {
            "booking_count": 5, "resolved_count": 4, "completed_count": 2, "cancelled_count": 1,
            "no_show_count": 1, "scheduled_count": 1, "collected_revenue_cents": 15000,
            "completion_rate_pct": 50, "cancellation_rate_pct": 25, "mean_lead_days": 3.6,
            "feedback_response_count": 2, "average_feedback_score": 4.5, "average_service_minutes": 45,
        }
        self.assertEqual(metrics, expected)

    def test_rejects_duplicate_id(self):
        rows = fixture()
        rows[1]["booking_id"] = rows[0]["booking_id"]
        with self.assertRaises(ValueError):
            self.read(rows)

    def test_rejects_unknown_service(self):
        self.assert_invalid(service_code="UNKNOWN")

    def test_rejects_invalid_date(self):
        for value in ["2026-02-30", "20260103", "03/01/2026"]:
            with self.subTest(value=value):
                self.assert_invalid(appointment_date=value)
        self.assert_invalid(created_date="2026-01-04")

    def test_rejects_overpayment(self):
        self.assert_invalid(paid_amount_cents="10001")
        self.assert_invalid(paid_amount_cents="10.5")

    def test_rejects_noncompleted_payment(self):
        rows = fixture()
        rows[2]["paid_amount_cents"] = "1"
        with self.assertRaises(ValueError):
            self.read(rows)

    def test_rejects_invalid_feedback(self):
        for score in ["0", "6", "4.5"]:
            with self.subTest(score=score):
                self.assert_invalid(satisfaction_score=score)
        rows = fixture()
        rows[3]["satisfaction_score"] = "4"
        with self.assertRaises(ValueError):
            self.read(rows)

    def test_rejects_noncompleted_actual_time(self):
        rows = fixture()
        rows[4]["actual_minutes"] = "30"
        with self.assertRaises(ValueError):
            self.read(rows)
        self.assert_invalid(actual_minutes="")

    def test_snapshot_rules(self):
        self.assert_invalid(appointment_date="2026-04-01")
        rows = fixture()
        rows[4]["appointment_date"] = "2026-03-31"
        with self.assertRaises(ValueError):
            self.read(rows)
        rows = fixture()
        rows[4].update(created_date="2026-04-05", appointment_date="2026-04-10")
        with self.assertRaises(ValueError):
            self.read(rows)

    def test_cancellation_reason_rules(self):
        self.assert_invalid(cancellation_reason="Not applicable")
        rows = fixture()
        rows[2]["cancellation_reason"] = " "
        with self.assertRaises(ValueError):
            self.read(rows)

    def test_missing_feedback_is_excluded(self):
        rows = fixture()
        rows[1]["satisfaction_score"] = ""
        metrics = pipeline.calculate_metrics(self.read(rows))
        self.assertEqual(metrics["average_feedback_score"], 4)
        self.assertEqual(metrics["feedback_response_count"], 1)

    def test_empty_and_scheduled_only_rates(self):
        empty = pipeline.calculate_metrics([])
        self.assertEqual(empty["booking_count"], 0)
        self.assertEqual(empty["collected_revenue_cents"], 0)
        self.assertIsNone(empty["completion_rate_pct"])
        self.assertIsNone(empty["average_feedback_score"])
        selected = pipeline.filter_rows(self.read(), {"status": "scheduled"})
        self.assertEqual(len(selected), 1)
        self.assertIsNone(pipeline.calculate_metrics(selected)["cancellation_rate_pct"])

    def test_group_reconciliation(self):
        rows = self.read()
        for field in ["month", "service_code", "channel"]:
            grouped = pipeline.grouped_summary(rows, field)
            self.assertEqual(sum(item["booking_count"] for item in grouped), 5)
            self.assertEqual(sum(item["collected_revenue_cents"] for item in grouped), 15000)
        filtered = pipeline.filter_rows(rows, {"service_code": "CLEAN", "month": "2026-01"})
        self.assertEqual(len(filtered), 3)
        self.assertEqual(pipeline.calculate_metrics(filtered)["collected_revenue_cents"], 10000)

    def test_build_outputs_and_rejection_policy(self):
        output = Path(self.directory.name) / "results"
        pipeline.build(self.write(fixture()), output, build_dashboard=False)
        expected = {"clean_bookings.csv", "kpis.csv", "monthly_summary.csv", "service_summary.csv", "channel_summary.csv", "validation_report.json"}
        self.assertEqual({path.name for path in output.iterdir()}, expected)
        report = json.loads((output / "validation_report.json").read_text())
        self.assertEqual(report["status"], "passed")
        self.assertEqual(report["row_count"], 5)
        invalid_output = Path(self.directory.name) / "must-not-exist"
        rows = fixture()
        rows[0]["paid_amount_cents"] = "999999"
        with self.assertRaises(ValueError):
            pipeline.build(self.write(rows), invalid_output, build_dashboard=False)
        self.assertFalse(invalid_output.exists())

    def test_documented_source_counts_and_independent_revenue(self):
        source = pipeline.ROOT / "data" / "bookings.csv"
        with source.open(encoding="utf-8", newline="") as handle:
            raw = list(csv.DictReader(handle))
        self.assertEqual(len(raw), 144)
        self.assertEqual(sum(row["status"] == "completed" for row in raw), 93)
        self.assertEqual(sum(row["status"] == "cancelled" for row in raw), 26)
        self.assertEqual(sum(row["status"] == "no_show" for row in raw), 13)
        self.assertEqual(sum(row["status"] == "scheduled" for row in raw), 12)
        expected_revenue = sum(int(row["paid_amount_cents"]) for row in raw if row["status"] == "completed")
        metrics = pipeline.calculate_metrics(pipeline.read_data(source))
        self.assertEqual(metrics["collected_revenue_cents"], expected_revenue)
        self.assertEqual(metrics["resolved_count"], 132)


if __name__ == "__main__":
    unittest.main()
