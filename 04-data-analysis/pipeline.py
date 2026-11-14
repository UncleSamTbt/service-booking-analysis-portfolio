"""Standard-library validation and reporting for an synthetic booking practice project."""
import argparse
import csv
from datetime import date
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_DATE = date(2026, 3, 31)
FIELDS = [
    "booking_id", "customer_id", "created_date", "appointment_date", "service_code",
    "customer_segment", "channel", "suburb", "technician_id", "status",
    "quoted_amount_cents", "paid_amount_cents", "scheduled_minutes", "actual_minutes",
    "satisfaction_score", "cancellation_reason",
]
SERVICES = {"CLEAN", "REPAIR", "GARDEN"}
STATUSES = {"completed", "cancelled", "no_show", "scheduled"}
CHANNELS = {"phone", "web", "messaging"}


class ValidationError(ValueError):
    """Invalid input is rejected before any analysis outputs are written."""


def _integer(value, field, minimum=0, maximum=None, optional=False):
    if optional and value == "":
        return None
    if not re.fullmatch(r"[0-9]+", value):
        raise ValidationError(f"{field}: expected an integer")
    number = int(value)
    if number < minimum or (maximum is not None and number > maximum):
        raise ValidationError(f"{field}: value outside permitted range")
    return number


def _date(value, field):
    if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
        raise ValidationError(f"{field}: expected YYYY-MM-DD")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValidationError(f"{field}: invalid calendar date") from exc


def read_data(path):
    """Read all rows, validate business rules, return typed rows with lead_days."""
    result = []
    seen = set()
    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, strict=True)
        if reader.fieldnames != FIELDS:
            raise ValidationError("CSV headers must match the documented 16-column schema and order")
        for line, raw in enumerate(reader, start=2):
            try:
                if None in raw or any(value is None for value in raw.values()):
                    raise ValidationError("Wrong number of fields")
                row = {key: value.strip() for key, value in raw.items()}
                if not re.fullmatch(r"B[0-9]{4}", row["booking_id"]):
                    raise ValidationError("booking_id: expected B followed by four digits")
                if row["booking_id"] in seen:
                    raise ValidationError("Duplicate booking_id")
                if not re.fullmatch(r"C[0-9]{3}", row["customer_id"]):
                    raise ValidationError("customer_id: invalid synthetic reference")
                if row["technician_id"] not in {"T01", "T02", "T03", "T04"}:
                    raise ValidationError("technician_id: unsupported reference")
                for field, valid in [
                    ("service_code", SERVICES), ("status", STATUSES), ("channel", CHANNELS),
                    ("customer_segment", {"household", "small_business"}),
                    ("suburb", {"Demo North", "Demo Central", "Demo South"}),
                ]:
                    if row[field] not in valid:
                        raise ValidationError(f"{field}: unsupported value")
                created = _date(row["created_date"], "created_date")
                appointment = _date(row["appointment_date"], "appointment_date")
                if created > SNAPSHOT_DATE:
                    raise ValidationError("created_date is after the reporting snapshot")
                if appointment < created:
                    raise ValidationError("appointment_date precedes created_date")
                is_scheduled = row["status"] == "scheduled"
                if is_scheduled != (appointment > SNAPSHOT_DATE):
                    raise ValidationError("status/date inconsistent with 2026-03-31 reporting snapshot")
                row["quoted_amount_cents"] = _integer(row["quoted_amount_cents"], "quoted_amount_cents", 1)
                row["paid_amount_cents"] = _integer(row["paid_amount_cents"], "paid_amount_cents", 0, row["quoted_amount_cents"])
                row["scheduled_minutes"] = _integer(row["scheduled_minutes"], "scheduled_minutes", 1)
                row["actual_minutes"] = _integer(row["actual_minutes"], "actual_minutes", 1, optional=True)
                row["satisfaction_score"] = _integer(row["satisfaction_score"], "satisfaction_score", 1, 5, optional=True)
                if row["status"] == "completed":
                    if row["actual_minutes"] is None:
                        raise ValidationError("completed booking requires positive actual_minutes")
                elif row["paid_amount_cents"] != 0 or row["actual_minutes"] is not None or row["satisfaction_score"] is not None:
                    raise ValidationError("non-completed booking must have zero payment and blank duration/feedback")
                if (row["status"] == "cancelled") != bool(row["cancellation_reason"]):
                    raise ValidationError("cancellation_reason is required only for cancelled bookings")
                row["lead_days"] = (appointment - created).days
                seen.add(row["booking_id"])
                result.append(row)
            except (ValueError, TypeError) as exc:
                raise ValidationError(f"CSV line {line}: {exc}") from exc
    return result


def _mean(values):
    return round(sum(values) / len(values), 6) if values else None


def calculate_metrics(rows):
    completed = [row for row in rows if row["status"] == "completed"]
    cancelled = sum(row["status"] == "cancelled" for row in rows)
    no_show = sum(row["status"] == "no_show" for row in rows)
    resolved = len(completed) + cancelled + no_show
    scores = [row["satisfaction_score"] for row in completed if row["satisfaction_score"] is not None]
    return {
        "booking_count": len(rows), "resolved_count": resolved,
        "completed_count": len(completed), "cancelled_count": cancelled,
        "no_show_count": no_show, "scheduled_count": len(rows) - resolved,
        "collected_revenue_cents": sum(row["paid_amount_cents"] for row in completed),
        "completion_rate_pct": round(len(completed) / resolved * 100, 6) if resolved else None,
        "cancellation_rate_pct": round(cancelled / resolved * 100, 6) if resolved else None,
        "mean_lead_days": _mean([row["lead_days"] for row in rows]),
        "feedback_response_count": len(scores), "average_feedback_score": _mean(scores),
        "average_service_minutes": _mean([row["actual_minutes"] for row in completed]),
    }


def filter_rows(rows, filters):
    allowed = {"service_code", "status", "channel", "month"}
    if set(filters) - allowed:
        raise ValueError("Unsupported filter key")
    return [row for row in rows if all(
        not value or (row["appointment_date"][:7] if key == "month" else row[key]) == value
        for key, value in filters.items()
    )]


def grouped_summary(rows, field):
    if field not in {"month", "service_code", "channel"}:
        raise ValueError("Unsupported grouping")
    key = lambda row: row["appointment_date"][:7] if field == "month" else row[field]
    values = sorted({key(row) for row in rows})
    return [{field: value, **calculate_metrics([row for row in rows if key(row) == value])} for value in values]


def _write_csv(path, fields, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def build(input_path, output_dir, build_dashboard=True):
    rows = read_data(input_path)
    metrics = calculate_metrics(rows)
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    _write_csv(destination / "clean_bookings.csv", FIELDS + ["lead_days"], rows)
    _write_csv(destination / "kpis.csv", ["metric", "value"], [{"metric": key, "value": value} for key, value in metrics.items()])
    for field, filename in [("month", "monthly_summary.csv"), ("service_code", "service_summary.csv"), ("channel", "channel_summary.csv")]:
        summary = grouped_summary(rows, field)
        _write_csv(destination / filename, [field] + list(metrics), summary)
    report = {
        "status": "passed", "source_filename": Path(input_path).name,
        "snapshot_date": SNAPSHOT_DATE.isoformat(), "row_count": len(rows),
        "rejected_rows": 0,
        "policy": "Reject the full input on any invalid row; never silently drop or repair data.",
        "passed_checks": ["exact schema", "unique IDs", "controlled values", "valid calendar dates", "date ordering", "snapshot consistency", "integer amounts", "payment within quote", "completed-only payment/duration/feedback", "feedback range", "cancellation reason"],
    }
    (destination / "validation_report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if build_dashboard:
        dashboard = ROOT / "05-business-intelligence"
        payload = {"snapshot_date": SNAPSHOT_DATE.isoformat(), "records": rows}
        cases = [
            ("all", {}), ("clean", {"service_code": "CLEAN"}),
            ("january", {"month": "2026-01"}), ("completed", {"status": "completed"}),
            ("scheduled", {"status": "scheduled"}), ("empty", {"month": "2099-01"}),
        ]
        baseline = [{"name": name, "filters": filters, "metrics": calculate_metrics(filter_rows(rows, filters))} for name, filters in cases]
        (dashboard / "dashboard_data.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        (dashboard / "metrics-baseline.json").write_text(json.dumps(baseline, indent=2) + "\n", encoding="utf-8")
        template = (dashboard / "dashboard.template.html").read_text(encoding="utf-8")
        javascript = (dashboard / "dashboard_metrics.js").read_text(encoding="utf-8")
        if template.count("__DATA_JSON__") != 1 or template.count("__METRICS_JS__") != 1:
            raise ValueError("Dashboard template must contain each documented placeholder exactly once")
        embedded = json.dumps(payload, separators=(",", ":")).replace("</", "<\\/")
        html = template.replace("__DATA_JSON__", embedded).replace("__METRICS_JS__", javascript)
        (dashboard / "dashboard.html").write_text(html, encoding="utf-8")
    return metrics


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=ROOT / "data" / "bookings.csv")
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).parent / "outputs")
    parser.add_argument("--skip-dashboard", action="store_true")
    args = parser.parse_args()
    try:
        metrics = build(args.input, args.output_dir, not args.skip_dashboard)
    except (OSError, ValueError, csv.Error) as exc:
        parser.exit(1, f"Validation/build failed: {exc}\n")
    print(f"Validated {metrics['booking_count']} records; collected revenue ZAR {metrics['collected_revenue_cents'] / 100:,.2f}")


if __name__ == "__main__":
    main()
