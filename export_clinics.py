#!/usr/bin/env python3
"""
Export clinics and their packages to a JSON file consumed by the frontend.

This script reuses the project's SQLAlchemy session and models so that the
output is always in sync with the API layer.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, List

from sqlalchemy.orm import Session

from app.database.db import SessionLocal
from app.database.entities import Clinic, Package


DEFAULT_OUTPUT = (
    Path(__file__).resolve().parent / "istanbulmedic-website-fe" / "src/data/clinics.json"
)


def _decimal_to_number(value: Decimal | None) -> float | None:
    if value is None:
        return None
    return float(value)


def _serialize_package(package: Package) -> Dict[str, Any]:
    return {
        "id": str(package.id),
        "name": package.name,
        "description": package.description,
        "price": _decimal_to_number(package.price),
        "currency": package.currency,
        "isActive": package.is_active,
    }


def _serialize_clinic(clinic: Clinic) -> Dict[str, Any]:
    packages = list(clinic.packages or [])
    package_payload = [_serialize_package(pkg) for pkg in packages]
    mirrored_ids = clinic.package_ids or [pkg.id for pkg in packages]
    package_ids = [str(pkg_id) for pkg_id in mirrored_ids]

    return {
        "id": str(clinic.id),
        "name": clinic.title or "Unknown Clinic",
        "hasContract": clinic.has_contract,
        "packageIds": package_ids,
        "packages": package_payload,
        "rating": float(clinic.rating) if clinic.rating is not None else None,
        "reviews": int(clinic.reviews_count or 0),
        "categories": clinic.categories or [],
        "address": clinic.location or clinic.address or "Address not available",
        "phone": clinic.phone or "Phone not available",
        "email": clinic.email or "",
        "website": clinic.website or "",
        "image": clinic.image_url or "/results/clinic_default.jpg",
        "opening_hours": clinic.opening_hours
        or {
            "monday": "9:00 AM - 6:00 PM",
            "tuesday": "9:00 AM - 6:00 PM",
            "wednesday": "9:00 AM - 6:00 PM",
            "thursday": "9:00 AM - 6:00 PM",
            "friday": "9:00 AM - 6:00 PM",
            "saturday": "9:00 AM - 4:00 PM",
            "sunday": "Closed",
        },
        "additional_info": clinic.additional_info
        or {
            "languages": ["English"],
            "payment_methods": ["Cash", "Credit Card"],
            "accommodation": "Hotel booking assistance available",
            "airport_transfer": "Airport transfer available",
        },
        "price_range": clinic.price_range or "Contact for pricing",
        "availability": clinic.availability or "Contact for availability",
        "country": clinic.country or "Unknown",
        "city": clinic.city or "Unknown",
        "updatedAt": clinic.updated_at.isoformat(),
    }


def export_clinics(session: Session) -> Dict[str, Any]:
    clinics = (
        session.query(Clinic)
        .order_by(Clinic.rating.desc().nullslast(), Clinic.reviews_count.desc().nullslast())
        .all()
    )

    payload = [_serialize_clinic(clinic) for clinic in clinics]
    return {
        "clinics": payload,
        "total": len(payload),
        "total_pages": 1,
        "exported_at": datetime.utcnow().isoformat(),
        "source": "postgres.clinics",
    }


def save_to_json(data: Dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def get_output_path(arg_value: str | None) -> Path:
    if arg_value:
        return Path(arg_value).expanduser().resolve()
    return DEFAULT_OUTPUT


def main() -> None:
    parser = argparse.ArgumentParser(description="Export clinics to JSON for the frontend.")
    parser.add_argument(
        "-o",
        "--output",
        dest="output",
        help="Optional output path. Defaults to istanbulmedic-website-fe/src/data/clinics.json",
    )
    args = parser.parse_args()

    session = SessionLocal()
    try:
        print("🚀 Exporting clinics...")
        payload = export_clinics(session)
        output_path = get_output_path(args.output)
        save_to_json(payload, output_path)
        print(f"✅ Exported {payload['total']} clinics to {output_path}")
        print(f"   Packages included for {sum(len(c['packages']) for c in payload['clinics'])} entries.")
    finally:
        session.close()


if __name__ == "__main__":
    main()



