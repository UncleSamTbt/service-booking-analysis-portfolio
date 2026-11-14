"""Create deterministic fictional booking records. No real customer data."""
import csv
from datetime import date, timedelta
from pathlib import Path
import random

FIELDS = [
    "booking_id", "customer_id", "created_date", "appointment_date", "service_code",
    "customer_segment", "channel", "suburb", "technician_id", "status",
    "quoted_amount_cents", "paid_amount_cents", "scheduled_minutes", "actual_minutes",
    "satisfaction_score", "cancellation_reason",
]


def generate(path=None):
    path = Path(path) if path else Path(__file__).with_name("bookings.csv")
    rng = random.Random(20260331)
    services = [("CLEAN", 45000, 90), ("REPAIR", 65000, 60), ("GARDEN", 55000, 120)]
    rows = []
    for i in range(144):
        scheduled = i >= 132
        appointment = date(2026, 4, i - 131) if scheduled else date(2026, 1, 1) + timedelta(days=(i * 7) % 89)
        service, quote, duration = services[i % 3]
        status = "scheduled" if scheduled else ("completed" if i % 10 < 7 else "cancelled" if i % 10 < 9 else "no_show")
        completed = status == "completed"
        rows.append({
            "booking_id": f"B{i + 1:04d}", "customer_id": f"C{i % 51 + 1:03d}",
            "created_date": min(appointment - timedelta(days=rng.randint(2, 18)), date(2026, 3, 31)).isoformat(),
            "appointment_date": appointment.isoformat(), "service_code": service,
            "customer_segment": "small_business" if i % 4 == 0 else "household",
            "channel": ["phone", "web", "messaging"][rng.randrange(3)],
            "suburb": ["Demo North", "Demo Central", "Demo South"][i % 3],
            "technician_id": f"T{i % 4 + 1:02d}", "status": status,
            "quoted_amount_cents": quote,
            "paid_amount_cents": quote - (1500 if i % 11 == 0 else 0) if completed else 0,
            "scheduled_minutes": duration,
            "actual_minutes": max(15, duration + rng.choice([-15, 0, 15, 30])) if completed else "",
            "satisfaction_score": rng.choice([3, 4, 4, 5, 5]) if completed and i % 5 else "",
            "cancellation_reason": "Customer unavailable" if status == "cancelled" else "",
        })
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    return path


if __name__ == "__main__":
    output = generate()
    print(f"Created 144 synthetic records: {output.name}")
