"use client";
import { useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";

interface MortgageResult {
  loan_amount: number;
  monthly_repayment: number;
  total_repayment: number;
  total_interest: number;
  affordability_ratio: number;
  affordability_status: string;
  max_affordable_price: number;
  currency: string;
}

interface ValuationResult {
  estimated_value: number;
  confidence_low: number;
  confidence_high: number;
  currency: string;
}

const CITIES = ["Nairobi","Mombasa","Lagos","Accra","Kampala","Dar es Salaam"];
const NEIGHBOURHOODS: Record<string, string[]> = {
  "Nairobi": ["Westlands","Karen","Kilimani","Lavington","Runda","Kasarani","Eastleigh"],
  "Mombasa": ["Nyali","Shanzu","Bamburi","Mtwapa"],
  "Lagos":   ["Lekki","Victoria Island","Ikoyi","Yaba","Ikeja"],
  "Accra":   ["East Legon","Cantonments","Airport Hills","Tema"],
  "Kampala": ["Kololo","Nakasero","Ntinda","Bukoto"],
  "Dar es Salaam": ["Msasani","Oyster Bay","Kinondoni","Mikocheni"],
};

const STATUS_COLORS: Record<string, string> = {
  comfortable: "text-green-600 bg-green-50",
  affordable:  "text-blue-600 bg-blue-50",
  stretched:   "text-yellow-600 bg-yellow-50",
  unaffordable:"text-red-600 bg-red-50",
};

export default function MortgagePage() {
  const [form, setForm] = useState({
    property_price: 5000000,
    deposit_amount: 1000000,
    loan_term_years: 20,
    annual_interest_rate: 13.5,
    monthly_income: 150000,
    currency: "KES",
  });

  const [valForm, setValForm] = useState({
    city: "Nairobi",
    neighbourhood: "Westlands",
    bedrooms: 3,
    floor_area_sqm: 120,
    property_type: "apartment",
    furnishing: "semi_furnished",
    price_period: "monthly",
  });

  const [result, setResult] = useState<MortgageResult | null>(null);
  const [valResult, setValResult] = useState<ValuationResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [valLoading, setValLoading] = useState(false);

  const handleCalculate = async () => {
    setLoading(true);
    try {
      const data = await api.calculateMortgage(form);
      setResult(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleValuation = async () => {
    setValLoading(true);
    try {
      const data = await api.getValuation({
        ...valForm,
        bathrooms: Math.max(1, valForm.bedrooms - 1),
        tier: 2,
        listing_month: new Date().getMonth() + 1,
        distance_to_cbd_km: 5,
        infrastructure_score: 7,
        transit_access_score: 7,
        amenity_count: 3,
      });
      setValResult(data);
    } catch (e) {
      console.error(e);
    } finally {
      setValLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navbar */}
      <nav className="bg-white border-b sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
          <Link href="/" className="text-xl font-bold text-primary-600">🏘 AfriProp</Link>
          <div className="hidden md:flex gap-6 text-sm text-gray-600">
            <Link href="/" className="hover:text-primary-600">Home</Link>
            <Link href="/search" className="hover:text-primary-600">Search</Link>
            <Link href="/mortgage" className="text-primary-600 font-medium">Mortgage</Link>
          </div>
        </div>
      </nav>

      <div className="max-w-6xl mx-auto px-4 py-10">
        <div className="text-center mb-10">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            💰 Mortgage & Affordability Calculator
          </h1>
          <p className="text-gray-500">
            Calculate your monthly repayments and check if a property is within your budget
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-8">
          {/* Mortgage Calculator */}
          <div className="card">
            <h2 className="text-xl font-bold text-gray-900 mb-6">Mortgage Calculator</h2>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Currency
                </label>
                <select
                  className="input"
                  value={form.currency}
                  onChange={(e) => setForm({...form, currency: e.target.value})}
                >
                  <option value="KES">KES — Kenyan Shilling</option>
                  <option value="NGN">NGN — Nigerian Naira</option>
                  <option value="GHS">GHS — Ghanaian Cedi</option>
                  <option value="UGX">UGX — Ugandan Shilling</option>
                  <option value="TZS">TZS — Tanzanian Shilling</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Property Price ({form.currency})
                </label>
                <input type="number" className="input"
                  value={form.property_price}
                  onChange={(e) => setForm({...form, property_price: Number(e.target.value)})}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Deposit Amount ({form.currency})
                </label>
                <input type="number" className="input"
                  value={form.deposit_amount}
                  onChange={(e) => setForm({...form, deposit_amount: Number(e.target.value)})}
                />
                <p className="text-xs text-gray-400 mt-1">
                  {((form.deposit_amount / form.property_price) * 100).toFixed(1)}% deposit
                </p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Loan Term (years)
                  </label>
                  <input type="number" className="input"
                    value={form.loan_term_years}
                    onChange={(e) => setForm({...form, loan_term_years: Number(e.target.value)})}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Interest Rate (% p.a.)
                  </label>
                  <input type="number" step="0.1" className="input"
                    value={form.annual_interest_rate}
                    onChange={(e) => setForm({...form, annual_interest_rate: Number(e.target.value)})}
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Monthly Income ({form.currency})
                </label>
                <input type="number" className="input"
                  value={form.monthly_income}
                  onChange={(e) => setForm({...form, monthly_income: Number(e.target.value)})}
                />
              </div>

              <button
                onClick={handleCalculate}
                disabled={loading}
                className="btn-primary w-full"
              >
                {loading ? "Calculating..." : "Calculate Mortgage"}
              </button>
            </div>

            {result && (
              <div className="mt-6 space-y-4">
                <div className="bg-primary-50 rounded-xl p-4 text-center">
                  <div className="text-sm text-gray-500 mb-1">Monthly Repayment</div>
                  <div className="text-3xl font-bold text-primary-600">
                    {result.currency} {result.monthly_repayment.toLocaleString()}
                  </div>
                </div>

                <div className={`rounded-xl p-3 text-center text-sm font-medium ${STATUS_COLORS[result.affordability_status] || "text-gray-600 bg-gray-50"}`}>
                  Affordability: {result.affordability_ratio.toFixed(1)}% of income —{" "}
                  <span className="capitalize">{result.affordability_status}</span>
                </div>

                <div className="grid grid-cols-2 gap-3 text-sm">
                  <div className="bg-gray-50 rounded-lg p-3">
                    <div className="text-gray-500 mb-1">Loan Amount</div>
                    <div className="font-bold">{result.currency} {result.loan_amount.toLocaleString()}</div>
                  </div>
                  <div className="bg-gray-50 rounded-lg p-3">
                    <div className="text-gray-500 mb-1">Total Interest</div>
                    <div className="font-bold text-red-500">{result.currency} {result.total_interest.toLocaleString()}</div>
                  </div>
                  <div className="bg-gray-50 rounded-lg p-3">
                    <div className="text-gray-500 mb-1">Total Repayment</div>
                    <div className="font-bold">{result.currency} {result.total_repayment.toLocaleString()}</div>
                  </div>
                  <div className="bg-gray-50 rounded-lg p-3">
                    <div className="text-gray-500 mb-1">Max Affordable</div>
                    <div className="font-bold text-green-600">{result.currency} {result.max_affordable_price.toLocaleString()}</div>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* AI Valuation */}
          <div className="card">
            <h2 className="text-xl font-bold text-gray-900 mb-2">🤖 AI Property Valuation</h2>
            <p className="text-gray-500 text-sm mb-6">
              Get an AI-estimated market value before making an offer
            </p>

            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">City</label>
                  <select className="input" value={valForm.city}
                    onChange={(e) => setValForm({...valForm, city: e.target.value, neighbourhood: NEIGHBOURHOODS[e.target.value]?.[0] || ""})}>
                    {CITIES.map((c) => <option key={c} value={c}>{c}</option>)}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Neighbourhood</label>
                  <select className="input" value={valForm.neighbourhood}
                    onChange={(e) => setValForm({...valForm, neighbourhood: e.target.value})}>
                    {(NEIGHBOURHOODS[valForm.city] || []).map((n) => <option key={n} value={n}>{n}</option>)}
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Bedrooms</label>
                  <select className="input" value={valForm.bedrooms}
                    onChange={(e) => setValForm({...valForm, bedrooms: Number(e.target.value)})}>
                    {[1,2,3,4,5].map((n) => <option key={n} value={n}>{n} bedroom{n>1?"s":""}</option>)}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Floor Area (m²)</label>
                  <input type="number" className="input" value={valForm.floor_area_sqm}
                    onChange={(e) => setValForm({...valForm, floor_area_sqm: Number(e.target.value)})} />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Property Type</label>
                  <select className="input" value={valForm.property_type}
                    onChange={(e) => setValForm({...valForm, property_type: e.target.value})}>
                    <option value="apartment">Apartment</option>
                    <option value="house">House</option>
                    <option value="bedsitter">Bedsitter</option>
                    <option value="commercial">Commercial</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Furnishing</label>
                  <select className="input" value={valForm.furnishing}
                    onChange={(e) => setValForm({...valForm, furnishing: e.target.value})}>
                    <option value="furnished">Furnished</option>
                    <option value="semi_furnished">Semi Furnished</option>
                    <option value="unfurnished">Unfurnished</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Price Period</label>
                <select className="input" value={valForm.price_period}
                  onChange={(e) => setValForm({...valForm, price_period: e.target.value})}>
                  <option value="monthly">Monthly Rental</option>
                  <option value="yearly">Yearly Rental</option>
                  <option value="once">Sale Price</option>
                </select>
              </div>

              <button onClick={handleValuation} disabled={valLoading} className="btn-primary w-full">
                {valLoading ? "Getting AI Valuation..." : "🤖 Get AI Valuation"}
              </button>
            </div>

            {valResult && (
              <div className="mt-6 space-y-4">
                <div className="bg-gradient-to-r from-primary-600 to-accent-500 rounded-xl p-5 text-white text-center">
                  <div className="text-sm opacity-80 mb-1">AI Estimated Market Value</div>
                  <div className="text-4xl font-bold mb-1">
                    {valResult.currency} {valResult.estimated_value.toLocaleString()}
                  </div>
                  <div className="text-sm opacity-70">
                    95% confidence interval
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3 text-sm">
                  <div className="bg-green-50 rounded-lg p-3 text-center">
                    <div className="text-gray-500 mb-1">Low Estimate</div>
                    <div className="font-bold text-green-600">
                      {valResult.currency} {valResult.confidence_low.toLocaleString()}
                    </div>
                  </div>
                  <div className="bg-blue-50 rounded-lg p-3 text-center">
                    <div className="text-gray-500 mb-1">High Estimate</div>
                    <div className="font-bold text-primary-600">
                      {valResult.currency} {valResult.confidence_high.toLocaleString()}
                    </div>
                  </div>
                </div>

                <div className="bg-gray-50 rounded-lg p-3 text-xs text-gray-500 text-center">
                  Powered by XGBoost • Trained on 50,000+ African properties •
                  R² = 0.996 • MAPE = 15.6%
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
