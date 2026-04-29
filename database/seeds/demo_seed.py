#!/usr/bin/env python3
"""
AfriProp Demo Seed Script
Populates the database with realistic demo data for hackathon demonstration.
Run from project root: python3 database/seeds/demo_seed.py
"""
import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import random
import uuid

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

# ── DATABASE CONNECTION ────────────────────────────────────────────────────────
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB   = os.getenv("POSTGRES_DB", "afriprop")
POSTGRES_USER = os.getenv("POSTGRES_USER", "afriprop")
POSTGRES_PASS = os.getenv("POSTGRES_PASSWORD", "changeme")

DATABASE_URL = (
    f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASS}"
    f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSession = async_sessionmaker(engine, expire_on_commit=False)

# ── SEED DATA ──────────────────────────────────────────────────────────────────

USERS = [
    {
        "id":              "seed-landlord-001",
        "full_name":       "James Kamau",
        "phone":           "+254711000001",
        "email":           "james.kamau@afriprop.demo",
        "hashed_password": "$2b$12$demo_hash_landlord_001",
        "role":            "landlord",
        "is_active":       True,
        "is_verified":     True,
    },
    {
        "id":              "seed-landlord-002",
        "full_name":       "Amina Hassan",
        "phone":           "+254711000002",
        "email":           "amina.hassan@afriprop.demo",
        "hashed_password": "$2b$12$demo_hash_landlord_002",
        "role":            "landlord",
        "is_active":       True,
        "is_verified":     True,
    },
    {
        "id":              "seed-tenant-001",
        "full_name":       "Brian Odhiambo",
        "phone":           "+254711000003",
        "email":           "brian.odhiambo@afriprop.demo",
        "hashed_password": "$2b$12$demo_hash_tenant_001",
        "role":            "tenant",
        "is_active":       True,
        "is_verified":     True,
    },
    {
        "id":              "seed-tenant-002",
        "full_name":       "Grace Wanjiru",
        "phone":           "+254711000004",
        "email":           "grace.wanjiru@afriprop.demo",
        "hashed_password": "$2b$12$demo_hash_tenant_002",
        "role":            "tenant",
        "is_active":       True,
        "is_verified":     True,
    },
    {
        "id":              "seed-agent-001",
        "full_name":       "David Mutua",
        "phone":           "+254711000005",
        "email":           "david.mutua@afriprop.demo",
        "hashed_password": "$2b$12$demo_hash_agent_001",
        "role":            "agent",
        "is_active":       True,
        "is_verified":     True,
    },
    {
        "id":              "seed-investor-001",
        "full_name":       "Sarah Otieno",
        "phone":           "+254711000006",
        "email":           "sarah.otieno@afriprop.demo",
        "hashed_password": "$2b$12$demo_hash_investor_001",
        "role":            "investor",
        "is_active":       True,
        "is_verified":     True,
    },
]

PROPERTIES = [
    # ── NAIROBI ───────────────────────────────────────────────────────────────
    {
        "id":                  "seed-prop-001",
        "landlord_id":         "seed-landlord-001",
        "title":               "Modern 2BR Apartment in Westlands",
        "description":         "Spacious apartment with stunning city views, modern kitchen, and secure parking. Located minutes from Westlands CBD with easy access to shopping malls and restaurants.",
        "property_type":       "apartment",
        "status":              "available",
        "bedrooms":            2,
        "bathrooms":           2,
        "floor_area_sqm":      85.0,
        "furnishing":          "semi_furnished",
        "price":               75000,
        "price_period":        "monthly",
        "currency":            "KES",
        "city":                "Nairobi",
        "neighbourhood":       "Westlands",
        "country":             "Kenya",
        "latitude":            -1.2676,
        "longitude":           36.8114,
        "verification_status": "verified",
        "is_active":           True,
        "is_featured":         True,
        "view_count":          142,
        "amenities": ["wifi", "parking", "security", "cctv", "balcony"],
    },
    {
        "id":                  "seed-prop-002",
        "landlord_id":         "seed-landlord-001",
        "title":               "Elegant 3BR House in Karen",
        "description":         "Beautiful family home in the serene Karen suburb. Features a large garden, separate servant quarters, borehole water supply, and 24-hour security.",
        "property_type":       "house",
        "status":              "available",
        "bedrooms":            3,
        "bathrooms":           3,
        "floor_area_sqm":      210.0,
        "furnishing":          "unfurnished",
        "price":               180000,
        "price_period":        "monthly",
        "currency":            "KES",
        "city":                "Nairobi",
        "neighbourhood":       "Karen",
        "country":             "Kenya",
        "latitude":            -1.3317,
        "longitude":           36.7073,
        "verification_status": "verified",
        "is_active":           True,
        "is_featured":         True,
        "view_count":          89,
        "amenities": ["parking", "security", "borehole", "generator", "cctv"],
    },
    {
        "id":                  "seed-prop-003",
        "landlord_id":         "seed-landlord-002",
        "title":               "Cosy 1BR Apartment in Kilimani",
        "description":         "Well-maintained apartment in prime Kilimani location. Walking distance to supermarkets, restaurants, and public transport. Ideal for young professionals.",
        "property_type":       "apartment",
        "status":              "available",
        "bedrooms":            1,
        "bathrooms":           1,
        "floor_area_sqm":      55.0,
        "furnishing":          "furnished",
        "price":               45000,
        "price_period":        "monthly",
        "currency":            "KES",
        "city":                "Nairobi",
        "neighbourhood":       "Kilimani",
        "country":             "Kenya",
        "latitude":            -1.2894,
        "longitude":           36.7820,
        "verification_status": "verified",
        "is_active":           True,
        "is_featured":         False,
        "view_count":          203,
        "amenities": ["wifi", "security", "balcony", "water"],
    },
    {
        "id":                  "seed-prop-004",
        "landlord_id":         "seed-landlord-002",
        "title":               "Bedsitter in Kasarani — Bills Included",
        "description":         "Affordable self-contained bedsitter with all bills included. Clean, safe compound with 24-hour security. Perfect for students and first-time renters.",
        "property_type":       "bedsitter",
        "status":              "available",
        "bedrooms":            0,
        "bathrooms":           1,
        "floor_area_sqm":      25.0,
        "furnishing":          "furnished",
        "price":               12000,
        "price_period":        "monthly",
        "currency":            "KES",
        "city":                "Nairobi",
        "neighbourhood":       "Kasarani",
        "country":             "Kenya",
        "latitude":            -1.2197,
        "longitude":           36.8979,
        "verification_status": "verified",
        "is_active":           True,
        "is_featured":         False,
        "view_count":          387,
        "amenities": ["water", "electricity", "security"],
    },
    {
        "id":                  "seed-prop-005",
        "landlord_id":         "seed-landlord-001",
        "title":               "4BR Luxury Villa in Runda",
        "description":         "Exquisite villa in prestigious Runda Estate. Features a swimming pool, home gym, smart home system, and landscaped gardens. Available for long-term lease.",
        "property_type":       "house",
        "status":              "available",
        "bedrooms":            4,
        "bathrooms":           4,
        "floor_area_sqm":      380.0,
        "furnishing":          "furnished",
        "price":               450000,
        "price_period":        "monthly",
        "currency":            "KES",
        "city":                "Nairobi",
        "neighbourhood":       "Runda",
        "country":             "Kenya",
        "latitude":            -1.2108,
        "longitude":           36.7897,
        "verification_status": "verified",
        "is_active":           True,
        "is_featured":         True,
        "view_count":          56,
        "amenities": ["pool", "gym", "parking", "security", "cctv", "generator", "borehole", "balcony"],
    },
    # ── MOMBASA ───────────────────────────────────────────────────────────────
    {
        "id":                  "seed-prop-006",
        "landlord_id":         "seed-landlord-002",
        "title":               "2BR Beachfront Apartment in Nyali",
        "description":         "Stunning apartment with direct ocean views in sought-after Nyali. Modern finishes, large balcony, swimming pool, and secure parking. Walk to the beach.",
        "property_type":       "apartment",
        "status":              "available",
        "bedrooms":            2,
        "bathrooms":           2,
        "floor_area_sqm":      95.0,
        "furnishing":          "furnished",
        "price":               65000,
        "price_period":        "monthly",
        "currency":            "KES",
        "city":                "Mombasa",
        "neighbourhood":       "Nyali",
        "country":             "Kenya",
        "latitude":            -4.0435,
        "longitude":           39.7184,
        "verification_status": "verified",
        "is_active":           True,
        "is_featured":         True,
        "view_count":          178,
        "amenities": ["pool", "parking", "security", "balcony", "wifi", "cctv"],
    },
    {
        "id":                  "seed-prop-007",
        "landlord_id":         "seed-landlord-001",
        "title":               "3BR House in Bamburi",
        "description":         "Spacious family home in quiet Bamburi residential area. Large compound, mature trees, and easy access to the beach and local amenities.",
        "property_type":       "house",
        "status":              "rented",
        "bedrooms":            3,
        "bathrooms":           2,
        "floor_area_sqm":      145.0,
        "furnishing":          "semi_furnished",
        "price":               40000,
        "price_period":        "monthly",
        "currency":            "KES",
        "city":                "Mombasa",
        "neighbourhood":       "Bamburi",
        "country":             "Kenya",
        "latitude":            -3.9875,
        "longitude":           39.7234,
        "verification_status": "verified",
        "is_active":           True,
        "is_featured":         False,
        "view_count":          94,
        "amenities": ["parking", "security", "water", "electricity"],
    },
    # ── LAGOS ─────────────────────────────────────────────────────────────────
    {
        "id":                  "seed-prop-008",
        "landlord_id":         "seed-landlord-002",
        "title":               "3BR Apartment in Lekki Phase 1",
        "description":         "Contemporary apartment in the heart of Lekki. Modern kitchen, en-suite bathrooms, 24-hour power supply with solar backup, and covered parking.",
        "property_type":       "apartment",
        "status":              "available",
        "bedrooms":            3,
        "bathrooms":           3,
        "floor_area_sqm":      135.0,
        "furnishing":          "semi_furnished",
        "price":               350000,
        "price_period":        "monthly",
        "currency":            "NGN",
        "city":                "Lagos",
        "neighbourhood":       "Lekki",
        "country":             "Nigeria",
        "latitude":            6.4698,
        "longitude":           3.5852,
        "verification_status": "verified",
        "is_active":           True,
        "is_featured":         True,
        "view_count":          234,
        "amenities": ["generator", "parking", "security", "cctv", "wifi"],
    },
    {
        "id":                  "seed-prop-009",
        "landlord_id":         "seed-landlord-001",
        "title":               "2BR Flat in Yaba — Close to University",
        "description":         "Well-located flat near University of Lagos. Reliable water supply, good road network, and close to shopping centres and transport hubs.",
        "property_type":       "apartment",
        "status":              "available",
        "bedrooms":            2,
        "bathrooms":           2,
        "floor_area_sqm":      75.0,
        "furnishing":          "unfurnished",
        "price":               120000,
        "price_period":        "monthly",
        "currency":            "NGN",
        "city":                "Lagos",
        "neighbourhood":       "Yaba",
        "country":             "Nigeria",
        "latitude":            6.5095,
        "longitude":           3.3711,
        "verification_status": "pending_review",
        "is_active":           True,
        "is_featured":         False,
        "view_count":          156,
        "amenities": ["water", "electricity", "security"],
    },
    # ── ACCRA ─────────────────────────────────────────────────────────────────
    {
        "id":                  "seed-prop-010",
        "landlord_id":         "seed-landlord-002",
        "title":               "4BR Executive House in East Legon",
        "description":         "Executive family home in prestigious East Legon. Fully furnished with high-end fittings, landscaped garden, staff quarters, and solar power system.",
        "property_type":       "house",
        "status":              "available",
        "bedrooms":            4,
        "bathrooms":           4,
        "floor_area_sqm":      320.0,
        "furnishing":          "furnished",
        "price":               8500,
        "price_period":        "monthly",
        "currency":            "GHS",
        "city":                "Accra",
        "neighbourhood":       "East Legon",
        "country":             "Ghana",
        "latitude":            5.6390,
        "longitude":           -0.1530,
        "verification_status": "verified",
        "is_active":           True,
        "is_featured":         True,
        "view_count":          112,
        "amenities": ["pool", "parking", "security", "generator", "cctv", "gym", "balcony"],
    },
    # ── COMMERCIAL ────────────────────────────────────────────────────────────
    {
        "id":                  "seed-prop-011",
        "landlord_id":         "seed-landlord-001",
        "title":               "Prime Office Space in Westlands",
        "description":         "Modern Grade-A office space in Westlands commercial hub. Open plan layout, fibre internet, backup generator, ample parking, and rooftop terrace.",
        "property_type":       "commercial",
        "status":              "available",
        "bedrooms":            0,
        "bathrooms":           4,
        "floor_area_sqm":      450.0,
        "furnishing":          "unfurnished",
        "price":               350000,
        "price_period":        "monthly",
        "currency":            "KES",
        "city":                "Nairobi",
        "neighbourhood":       "Westlands",
        "country":             "Kenya",
        "latitude":            -1.2659,
        "longitude":           36.8094,
        "verification_status": "verified",
        "is_active":           True,
        "is_featured":         True,
        "view_count":          67,
        "amenities": ["wifi", "parking", "security", "generator", "cctv"],
    },
    # ── FOR SALE ──────────────────────────────────────────────────────────────
    {
        "id":                  "seed-prop-012",
        "landlord_id":         "seed-landlord-002",
        "title":               "3BR Apartment For Sale — Kilimani",
        "description":         "Excellent investment opportunity. Well-maintained apartment in prime Kilimani. Currently tenanted at KES 55,000/month. Title deed available.",
        "property_type":       "apartment",
        "status":              "available",
        "bedrooms":            3,
        "bathrooms":           2,
        "floor_area_sqm":      110.0,
        "furnishing":          "semi_furnished",
        "price":               12500000,
        "price_period":        "once",
        "currency":            "KES",
        "city":                "Nairobi",
        "neighbourhood":       "Kilimani",
        "country":             "Kenya",
        "latitude":            -1.2901,
        "longitude":           36.7834,
        "verification_status": "verified",
        "is_active":           True,
        "is_featured":         True,
        "view_count":          298,
        "amenities": ["parking", "security", "balcony", "cctv"],
    },
]

AMENITY_MAP = {
    "wifi": "wifi", "parking": "parking", "pool": "pool",
    "gym": "gym", "security": "security", "water": "water",
    "electricity": "electricity", "generator": "generator",
    "borehole": "borehole", "cctv": "cctv", "balcony": "balcony",
    "pet_friendly": "pet_friendly",
}

LEDGER_ENTRIES = [
    {
        "id":          "seed-ledger-001",
        "tenant_id":   "seed-tenant-001",
        "landlord_id": "seed-landlord-001",
        "property_id": "seed-prop-001",
        "month_year":  "2026-02",
        "due_date":    datetime(2026, 2, 1),
        "amount_due":  75000,
        "amount_paid": 75000,
        "balance":     0,
        "status":      "paid",
    },
    {
        "id":          "seed-ledger-002",
        "tenant_id":   "seed-tenant-001",
        "landlord_id": "seed-landlord-001",
        "property_id": "seed-prop-001",
        "month_year":  "2026-03",
        "due_date":    datetime(2026, 3, 1),
        "amount_due":  75000,
        "amount_paid": 75000,
        "balance":     0,
        "status":      "paid",
    },
    {
        "id":          "seed-ledger-003",
        "tenant_id":   "seed-tenant-001",
        "landlord_id": "seed-landlord-001",
        "property_id": "seed-prop-001",
        "month_year":  "2026-04",
        "due_date":    datetime(2026, 4, 1),
        "amount_due":  75000,
        "amount_paid": 0,
        "balance":     75000,
        "status":      "pending",
    },
    {
        "id":          "seed-ledger-004",
        "tenant_id":   "seed-tenant-002",
        "landlord_id": "seed-landlord-002",
        "property_id": "seed-prop-003",
        "month_year":  "2026-03",
        "due_date":    datetime(2026, 3, 1),
        "amount_due":  45000,
        "amount_paid": 30000,
        "balance":     15000,
        "status":      "partial",
    },
    {
        "id":          "seed-ledger-005",
        "tenant_id":   "seed-tenant-002",
        "landlord_id": "seed-landlord-002",
        "property_id": "seed-prop-003",
        "month_year":  "2026-04",
        "due_date":    datetime(2026, 4, 1),
        "amount_due":  45000,
        "amount_paid": 0,
        "balance":     45000,
        "status":      "overdue",
    },
]

PAYMENTS = [
    {
        "id":                    "seed-payment-001",
        "tenant_id":             "seed-tenant-001",
        "landlord_id":           "seed-landlord-001",
        "property_id":           "seed-prop-001",
        "amount":                75000,
        "currency":              "KES",
        "payment_method":        "mpesa",
        "status":                "completed",
        "mpesa_receipt_number":  "QKA12BC34D",
        "reference_code":        "AFRIPROP-FEB2026-001",
        "description":           "Rent February 2026",
        "paid_at":               datetime(2026, 2, 1, 10, 23, 45),
    },
    {
        "id":                    "seed-payment-002",
        "tenant_id":             "seed-tenant-001",
        "landlord_id":           "seed-landlord-001",
        "property_id":           "seed-prop-001",
        "amount":                75000,
        "currency":              "KES",
        "payment_method":        "mpesa",
        "status":                "completed",
        "mpesa_receipt_number":  "QKB45DE67F",
        "reference_code":        "AFRIPROP-MAR2026-001",
        "description":           "Rent March 2026",
        "paid_at":               datetime(2026, 3, 1, 9, 15, 22),
    },
    {
        "id":                    "seed-payment-003",
        "tenant_id":             "seed-tenant-002",
        "landlord_id":           "seed-landlord-002",
        "property_id":           "seed-prop-003",
        "amount":                30000,
        "currency":              "KES",
        "payment_method":        "mpesa",
        "status":                "completed",
        "mpesa_receipt_number":  "QKC78GH90I",
        "reference_code":        "AFRIPROP-MAR2026-002",
        "description":           "Partial rent March 2026",
        "paid_at":               datetime(2026, 3, 3, 14, 30, 0),
    },
]

INVESTMENT_PROPERTIES = [
    {
        "id":                 "seed-invest-prop-001",
        "property_id":        "seed-prop-011",
        "title":              "Westlands Office Complex — Series A",
        "description":        "Prime Grade-A office space in Westlands. Fully leased to corporate tenants on 3-year contracts. Stable monthly income with strong capital appreciation prospects.",
        "total_value":        80000000,
        "total_units":        16000,
        "unit_price":         5000,
        "currency":           "KES",
        "units_sold":         4200,
        "units_available":    11800,
        "minimum_investment": 1,
        "expected_roi_pct":   14.5,
        "status":             "open",
    },
    {
        "id":                 "seed-invest-prop-002",
        "property_id":        "seed-prop-002",
        "title":              "Karen Residential Estate — Block B",
        "description":        "High-end residential units in Karen. Strong rental demand from expatriates and senior executives. Projected 12% annual returns with quarterly distributions.",
        "total_value":        120000000,
        "total_units":        24000,
        "unit_price":         5000,
        "currency":           "KES",
        "units_sold":         8750,
        "units_available":    15250,
        "minimum_investment": 1,
        "expected_roi_pct":   12.0,
        "status":             "open",
    },
]

INVESTMENTS = [
    {
        "id":                      "seed-investment-001",
        "investor_id":             "seed-investor-001",
        "investment_property_id":  "seed-invest-prop-001",
        "units_purchased":         100,
        "amount_invested":         500000,
        "currency":                "KES",
        "ownership_pct":           0.625,
        "monthly_income_share":    6041.67,
        "payment_id":              "seed-payment-001",
        "status":                  "active",
        "purchased_at":            datetime(2026, 1, 15),
    },
    {
        "id":                      "seed-investment-002",
        "investor_id":             "seed-investor-001",
        "investment_property_id":  "seed-invest-prop-002",
        "units_purchased":         50,
        "amount_invested":         250000,
        "currency":                "KES",
        "ownership_pct":           0.208,
        "monthly_income_share":    2500.0,
        "payment_id":              "seed-payment-002",
        "status":                  "active",
        "purchased_at":            datetime(2026, 2, 10),
        },
]


async def seed_users(session):
    from sqlalchemy import text
    print("  Seeding users...")
    for user in USERS:
        await session.execute(text("""
            INSERT INTO users (id, full_name, phone, email, hashed_password,
                               role, is_active, is_verified, created_at, updated_at)
            VALUES (:id, :full_name, :phone, :email, :hashed_password,
                    :role, :is_active, :is_verified, NOW(), NOW())
            ON CONFLICT (id) DO NOTHING
        """), user)
    print(f"  ✓ {len(USERS)} users seeded")


async def seed_properties(session):
    from sqlalchemy import text
    print("  Seeding properties...")
    for prop in PROPERTIES:
        amenities = prop.pop("amenities", [])
        await session.execute(text("""
            INSERT INTO properties (
                id, landlord_id, title, description, property_type, status,
                bedrooms, bathrooms, floor_area_sqm, furnishing, price,
                price_period, currency, city, neighbourhood, country,
                latitude, longitude, verification_status, is_active,
                is_featured, view_count, needs_review, created_at, updated_at
            ) VALUES (
                :id, :landlord_id, :title, :description, :property_type, :status,
                :bedrooms, :bathrooms, :floor_area_sqm, :furnishing, :price,
                :price_period, :currency, :city, :neighbourhood, :country,
                :latitude, :longitude, :verification_status, :is_active,
                :is_featured, :view_count, false, NOW(), NOW()
            ) ON CONFLICT (id) DO NOTHING
        """), {**prop, "furnishing": prop.get("furnishing", "unfurnished")})

        for amenity in amenities:
            await session.execute(text("""
                INSERT INTO property_amenities (id, property_id, amenity)
                VALUES (:id, :property_id, :amenity)
                ON CONFLICT DO NOTHING
            """), {
                "id":          str(uuid.uuid4()),
                "property_id": prop["id"],
                "amenity":     amenity,
            })
    print(f"  ✓ {len(PROPERTIES)} properties seeded with amenities")


async def seed_ledger(session):
    from sqlalchemy import text
    print("  Seeding rent ledger...")
    for entry in LEDGER_ENTRIES:
        await session.execute(text("""
            INSERT INTO rent_ledger (
                id, tenant_id, landlord_id, property_id, month_year,
                due_date, amount_due, amount_paid, balance, status,
                created_at, updated_at
            ) VALUES (
                :id, :tenant_id, :landlord_id, :property_id, :month_year,
                :due_date, :amount_due, :amount_paid, :balance, :status,
                NOW(), NOW()
            ) ON CONFLICT (id) DO NOTHING
        """), entry)
    print(f"  ✓ {len(LEDGER_ENTRIES)} ledger entries seeded")


async def seed_payments(session):
    from sqlalchemy import text
    print("  Seeding payments...")
    for payment in PAYMENTS:
        await session.execute(text("""
            INSERT INTO payments (
                id, tenant_id, landlord_id, property_id, amount, currency,
                payment_method, status, mpesa_receipt_number, reference_code,
                description, paid_at, created_at, updated_at
            ) VALUES (
                :id, :tenant_id, :landlord_id, :property_id, :amount, :currency,
                :payment_method, :status, :mpesa_receipt_number, :reference_code,
                :description, :paid_at, NOW(), NOW()
            ) ON CONFLICT (id) DO NOTHING
        """), payment)
    print(f"  ✓ {len(PAYMENTS)} payments seeded")


async def seed_investments(session):
    from sqlalchemy import text
    print("  Seeding investment properties...")
    for inv_prop in INVESTMENT_PROPERTIES:
        await session.execute(text("""
            INSERT INTO investment_properties (
                id, property_id, title, description, total_value, total_units,
                unit_price, currency, units_sold, units_available,
                minimum_investment, expected_roi_pct, status,
                created_at, updated_at
            ) VALUES (
                :id, :property_id, :title, :description, :total_value, :total_units,
                :unit_price, :currency, :units_sold, :units_available,
                :minimum_investment, :expected_roi_pct, :status,
                NOW(), NOW()
            ) ON CONFLICT (id) DO NOTHING
        """), inv_prop)

    print("  Seeding investor holdings...")
    for inv in INVESTMENTS:
        await session.execute(text("""
            INSERT INTO investments (
                id, investor_id, investment_property_id, units_purchased,
                amount_invested, currency, ownership_pct, monthly_income_share,
                payment_id, status, purchased_at, created_at
            ) VALUES (
                :id, :investor_id, :investment_property_id, :units_purchased,
                :amount_invested, :currency, :ownership_pct, :monthly_income_share,
                :payment_id, :status, :purchased_at, NOW()
            ) ON CONFLICT (id) DO NOTHING
        """), inv)
    print(f"  ✓ {len(INVESTMENT_PROPERTIES)} investment properties seeded")
    print(f"  ✓ {len(INVESTMENTS)} investor holdings seeded")


async def main():
    print("\n AfriProp Demo Seed Script")
    print("=" * 45)
    print(f"  Database: {POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}")
    print("=" * 45)

    async with AsyncSession() as session:
        async with session.begin():
            await seed_users(session)
            await seed_properties(session)
            await seed_ledger(session)
            await seed_payments(session)
            await seed_investments(session)

    print("=" * 45)
    print("  Demo data seeded successfully!")
    print("\n  Users:")
    for u in USERS:
        print(f"    {u['role']:10s} — {u['full_name']:20s} {u['phone']}")
    print(f"\n  Properties: {len(PROPERTIES)} across Nairobi, Mombasa, Lagos, Accra")
    print(f"  Ledger entries: {len(LEDGER_ENTRIES)}")
    print(f"  Payments: {len(PAYMENTS)}")
    print(f"  Investment properties: {len(INVESTMENT_PROPERTIES)}")
    print(f"  Investor holdings: {len(INVESTMENTS)}")
    print("=" * 45)
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
