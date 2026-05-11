"use client";
import { useState, useEffect } from "react";
import Link from "next/link";
import { api } from "@/lib/api";

interface Investment {
  id: string;
  investment_property_id: string;
  units_purchased: number;
  amount_invested: number;
  currency: string;
  ownership_pct: number;
  monthly_income_share: number;
  status: string;
  purchased_at: string;
}

interface InvestmentProperty {
  id: string;
  title: string;
  description: string;
  total_value: number;
  total_units: number;
  unit_price: number;
  currency: string;
  units_sold: number;
  units_available: number;
  expected_roi_pct: number;
  status: string;
}

export default function InvestorDashboard() {
  const [investments, setInvestments] = useState<Investment[]>([]);
  const [opportunities, setOpportunities] = useState<InvestmentProperty[]>([]);
  const [loading, setLoading] = useState(true);
  const DEMO_INVESTOR = "seed-investor-001";

  useEffect(() => {
    Promise.all([
      fetch(`http://localhost:8000/api/v1/finance/investments/portfolio/${DEMO_INVESTOR}`)
        .then(r => r.json()),
      api.getInvestments(),
    ]).then(([inv, opp]) => {
      setInvestments(Array.isArray(inv) ? inv : []);
      setOpportunities(Array.isArray(opp) ? opp : []);
    }).catch(console.error)
    .finally(() => setLoading(false));
  }, []);

  const totalInvested      = investments.reduce((s, i) => s + i.amount_invested, 0);
  const totalMonthlyIncome = investments.reduce((s, i) => s + i.monthly_income_share, 0);
  const totalOwnership     = investments.reduce((s, i) => s + i.ownership_pct, 0);

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white border-b sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
          <Link href="/" className="text-xl font-bold text-primary-600">🏘 AfriProp</Link>
          <div className="flex gap-4 text-sm">
            <Link href="/dashboard/tenant" className="text-gray-500 hover:text-primary-600">Tenant</Link>
            <Link href="/dashboard/landlord" className="text-gray-500 hover:text-primary-600">Landlord</Link>
            <span className="text-primary-600 font-medium">Investor</span>
          </div>
        </div>
      </nav>

      <div className="max-w-6xl mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-gray-900">💼 Investor Dashboard</h1>
          <p className="text-gray-500">Sarah Otieno — Portfolio Overview</p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <div className="card text-center">
            <div className="text-2xl font-bold text-primary-600">
              KES {totalInvested.toLocaleString()}
            </div>
            <div className="text-gray-500 text-sm">Total Invested</div>
          </div>
          <div className="card text-center">
            <div className="text-2xl font-bold text-accent-500">
              KES {totalMonthlyIncome.toLocaleString()}
            </div>
            <div className="text-gray-500 text-sm">Monthly Income</div>
          </div>
          <div className="card text-center">
            <div className="text-2xl font-bold text-primary-600">
              {totalOwnership.toFixed(3)}%
            </div>
            <div className="text-gray-500 text-sm">Total Ownership</div>
          </div>
          <div className="card text-center">
            <div className="text-2xl font-bold text-amber-500">
              {investments.length}
            </div>
            <div className="text-gray-500 text-sm">Properties Owned</div>
          </div>
        </div>

        <div className="grid md:grid-cols-2 gap-8">
          {/* My Portfolio */}
          <div>
            <h2 className="text-lg font-bold text-gray-900 mb-4">My Holdings</h2>
            {loading ? (
              <div className="card animate-pulse h-32" />
            ) : investments.length === 0 ? (
              <div className="card text-center text-gray-400 py-8">
                <div className="text-3xl mb-2">💰</div>
                <p>No investments yet</p>
              </div>
            ) : (
              <div className="space-y-4">
                {investments.map((inv) => (
                  <div key={inv.id} className="card">
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <div className="font-semibold text-gray-900">
                          {inv.units_purchased} units purchased
                        </div>
                        <div className="text-sm text-gray-500">
                          {new Date(inv.purchased_at).toLocaleDateString()}
                        </div>
                      </div>
                      <span className="bg-green-100 text-green-700 text-xs px-2 py-1 rounded-full">
                        {inv.status}
                      </span>
                    </div>
                    <div className="grid grid-cols-3 gap-3 text-sm">
                      <div className="bg-gray-50 rounded-lg p-2 text-center">
                        <div className="font-bold text-primary-600">
                          {inv.currency} {inv.amount_invested.toLocaleString()}
                        </div>
                        <div className="text-gray-400 text-xs">Invested</div>
                      </div>
                      <div className="bg-gray-50 rounded-lg p-2 text-center">
                        <div className="font-bold text-accent-500">
                          {inv.currency} {inv.monthly_income_share.toLocaleString()}
                        </div>
                        <div className="text-gray-400 text-xs">Monthly</div>
                      </div>
                      <div className="bg-gray-50 rounded-lg p-2 text-center">
                        <div className="font-bold text-amber-500">
                          {inv.ownership_pct.toFixed(3)}%
                        </div>
                        <div className="text-gray-400 text-xs">Ownership</div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Investment Opportunities */}
          <div>
            <h2 className="text-lg font-bold text-gray-900 mb-4">Open Opportunities</h2>
            <div className="space-y-4">
              {opportunities.map((opp) => {
                const pctSold = (opp.units_sold / opp.total_units) * 100;
                return (
                  <div key={opp.id} className="card">
                    <div className="flex items-start justify-between mb-2">
                      <h3 className="font-semibold text-gray-900 text-sm">{opp.title}</h3>
                      <span className="text-accent-500 font-bold text-sm">
                        {opp.expected_roi_pct}% ROI
                      </span>
                    </div>
                    <p className="text-gray-500 text-xs mb-3 line-clamp-2">{opp.description}</p>

                    {/* Progress bar */}
                    <div className="mb-3">
                      <div className="flex justify-between text-xs text-gray-500 mb-1">
                        <span>{pctSold.toFixed(1)}% funded</span>
                        <span>{opp.units_available.toLocaleString()} units left</span>
                      </div>
                      <div className="w-full bg-gray-100 rounded-full h-2">
                        <div
                          className="bg-primary-600 h-2 rounded-full"
                          style={{ width: `${pctSold}%` }}
                        />
                      </div>
                    </div>

                    <div className="flex items-center justify-between">
                      <div className="text-sm">
                        <span className="font-bold text-primary-600">
                          {opp.currency} {opp.unit_price.toLocaleString()}
                        </span>
                        <span className="text-gray-400"> / unit</span>
                      </div>
                      <button className="btn-primary text-xs px-3 py-1">
                        Invest Now
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
