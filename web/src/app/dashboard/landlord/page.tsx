"use client";
import { useState, useEffect } from "react";
import Link from "next/link";

interface Property {
  id: string;
  title: string;
  city: string;
  neighbourhood: string;
  price: number;
  currency: string;
  price_period: string;
  status: string;
  bedrooms: number;
  property_type: string;
  verification_status: string;
  view_count: number;
  is_featured: boolean;
}

interface LedgerEntry {
  id: string;
  tenant_id: string;
  property_id: string;
  month_year: string;
  amount_due: number;
  amount_paid: number;
  balance: number;
  status: string;
}

const STATUS_COLORS: Record<string, string> = {
  available:   "bg-green-100 text-green-700",
  rented:      "bg-blue-100 text-blue-700",
  sold:        "bg-gray-100 text-gray-700",
  under_offer: "bg-yellow-100 text-yellow-700",
};

const VERIFICATION_COLORS: Record<string, string> = {
  verified:       "bg-green-100 text-green-700",
  pending_review: "bg-yellow-100 text-yellow-700",
  unverified:     "bg-gray-100 text-gray-600",
  rejected:       "bg-red-100 text-red-700",
};

export default function LandlordDashboard() {
  const [properties, setProperties] = useState<Property[]>([]);
  const [ledger, setLedger] = useState<LedgerEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const DEMO_LANDLORD = "seed-landlord-001";
  const API = "http://localhost:8000";

  useEffect(() => {
    Promise.all([
      fetch(`${API}/api/v1/properties/my/listings?landlord_id=${DEMO_LANDLORD}`).then(r => r.json()),
      fetch(`${API}/api/v1/finance/payments/ledger/seed-prop-001`).then(r => r.json()),
    ]).then(([props, led]) => {
      setProperties(Array.isArray(props) ? props : []);
      setLedger(Array.isArray(led) ? led : []);
    }).catch(console.error)
    .finally(() => setLoading(false));
  }, []);

  const totalMonthlyRent = properties
    .filter(p => p.status === "rented" && p.price_period === "monthly")
    .reduce((s, p) => s + p.price, 0);
  const availableCount = properties.filter(p => p.status === "available").length;
  const rentedCount    = properties.filter(p => p.status === "rented").length;
  const totalViews     = properties.reduce((s, p) => s + p.view_count, 0);

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white border-b sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
          <Link href="/" className="text-xl font-bold text-primary-600">🏘 AfriProp</Link>
          <div className="flex gap-4 text-sm">
            <Link href="/dashboard/tenant" className="text-gray-500 hover:text-primary-600">Tenant</Link>
            <span className="text-primary-600 font-medium">Landlord</span>
            <Link href="/dashboard/investor" className="text-gray-500 hover:text-primary-600">Investor</Link>
          </div>
        </div>
      </nav>

      <div className="max-w-6xl mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-gray-900">🏢 Landlord Dashboard</h1>
          <p className="text-gray-500">James Kamau — Portfolio Management</p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <div className="card text-center">
            <div className="text-2xl font-bold text-primary-600">{properties.length}</div>
            <div className="text-gray-500 text-sm">Total Properties</div>
          </div>
          <div className="card text-center">
            <div className="text-2xl font-bold text-accent-500">{rentedCount}</div>
            <div className="text-gray-500 text-sm">Currently Rented</div>
          </div>
          <div className="card text-center">
            <div className="text-2xl font-bold text-amber-500">{availableCount}</div>
            <div className="text-gray-500 text-sm">Available</div>
          </div>
          <div className="card text-center">
            <div className="text-2xl font-bold text-primary-600">{totalViews}</div>
            <div className="text-gray-500 text-sm">Total Views</div>
          </div>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          {/* Properties List */}
          <div className="md:col-span-2">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-bold text-gray-900">My Properties</h2>
              <Link href="/" className="btn-primary text-sm">+ Add Property</Link>
            </div>

            {loading ? (
              <div className="space-y-3">
                {[1,2,3].map(i => <div key={i} className="card animate-pulse h-24" />)}
              </div>
            ) : (
              <div className="space-y-3">
                {properties.map((prop) => (
                  <Link key={prop.id} href={`/property/${prop.id}`}>
                    <div className="card hover:shadow-md transition-shadow cursor-pointer">
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex-1 min-w-0">
                          <h3 className="font-semibold text-gray-900 text-sm line-clamp-1">
                            {prop.title}
                          </h3>
                          <p className="text-xs text-gray-500">
                            📍 {prop.neighbourhood}, {prop.city}
                          </p>
                        </div>
                        <div className="flex gap-1 ml-2 flex-shrink-0">
                          <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${STATUS_COLORS[prop.status] || "bg-gray-100 text-gray-600"}`}>
                            {prop.status.replace("_"," ")}
                          </span>
                          <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${VERIFICATION_COLORS[prop.verification_status] || ""}`}>
                            {prop.verification_status === "verified" ? "✓" : "?"}
                          </span>
                        </div>
                      </div>
                      <div className="flex items-center justify-between text-sm">
                        <div className="flex gap-3 text-gray-500">
                          <span>🛏 {prop.bedrooms}BR</span>
                          <span className="capitalize">📦 {prop.property_type}</span>
                          <span>👁 {prop.view_count}</span>
                        </div>
                        <div className="font-bold text-primary-600">
                          {prop.currency} {prop.price.toLocaleString()}
                          <span className="text-gray-400 font-normal text-xs">
                            /{prop.price_period === "monthly" ? "mo" : prop.price_period}
                          </span>
                        </div>
                      </div>
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </div>

          {/* Rent Collection */}
          <div>
            <h2 className="text-lg font-bold text-gray-900 mb-4">Rent Collection</h2>
            <div className="card mb-4 text-center bg-gradient-to-br from-primary-600 to-primary-900 text-white">
              <div className="text-sm opacity-80 mb-1">Monthly Rental Income</div>
              <div className="text-3xl font-bold">
                KES {totalMonthlyRent.toLocaleString()}
              </div>
              <div className="text-xs opacity-60 mt-1">from {rentedCount} rented properties</div>
            </div>

            <div className="space-y-3">
              {ledger.map((entry) => (
                <div key={entry.id} className="card">
                  <div className="flex justify-between items-center mb-2">
                    <span className="font-semibold text-sm">{entry.month_year}</span>
                    <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                      entry.status === "paid" ? "bg-green-100 text-green-700" :
                      entry.status === "partial" ? "bg-yellow-100 text-yellow-700" :
                      entry.status === "overdue" ? "bg-red-100 text-red-700" :
                      "bg-gray-100 text-gray-600"
                    }`}>
                      {entry.status.toUpperCase()}
                    </span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <div>
                      <div className="text-gray-500 text-xs">Expected</div>
                      <div className="font-medium">KES {entry.amount_due.toLocaleString()}</div>
                    </div>
                    <div>
                      <div className="text-gray-500 text-xs">Received</div>
                      <div className="font-medium text-accent-500">
                        KES {entry.amount_paid.toLocaleString()}
                      </div>
                    </div>
                    <div>
                      <div className="text-gray-500 text-xs">Balance</div>
                      <div className={`font-medium ${entry.balance > 0 ? "text-red-500" : "text-accent-500"}`}>
                        KES {entry.balance.toLocaleString()}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
