"use client";
import { useState, useEffect } from "react";
import Link from "next/link";

interface LedgerEntry {
  id: string;
  month_year: string;
  due_date: string;
  amount_due: number;
  amount_paid: number;
  balance: number;
  status: string;
  currency?: string;
}

interface Payment {
  id: string;
  amount: number;
  currency: string;
  payment_method: string;
  status: string;
  mpesa_receipt_number: string;
  description: string;
  paid_at: string;
  reference_code: string;
}

const STATUS_COLORS: Record<string, string> = {
  paid:    "bg-green-100 text-green-700",
  partial: "bg-yellow-100 text-yellow-700",
  pending: "bg-blue-100 text-blue-700",
  overdue: "bg-red-100 text-red-700",
};

export default function TenantDashboard() {
  const [ledger, setLedger] = useState<LedgerEntry[]>([]);
  const [payments, setPayments] = useState<Payment[]>([]);
  const [loading, setLoading] = useState(true);
  const DEMO_PROPERTY = "seed-prop-001";
  const DEMO_TENANT   = "seed-tenant-001";
  const API           = "http://localhost:8000";

  useEffect(() => {
    Promise.all([
      fetch(`${API}/api/v1/finance/payments/ledger/${DEMO_PROPERTY}`).then(r => r.json()),
      fetch(`${API}/api/v1/finance/payments/history/${DEMO_TENANT}`).then(r => r.json()),
    ]).then(([l, p]) => {
      setLedger(Array.isArray(l) ? l : []);
      setPayments(Array.isArray(p) ? p : []);
    }).catch(console.error)
    .finally(() => setLoading(false));
  }, []);

  const totalPaid    = payments.filter(p => p.status === "completed").reduce((s, p) => s + p.amount, 0);
  const totalDue     = ledger.reduce((s, l) => s + l.amount_due, 0);
  const totalBalance = ledger.reduce((s, l) => s + l.balance, 0);

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white border-b sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
          <Link href="/" className="text-xl font-bold text-primary-600">🏘 AfriProp</Link>
          <div className="flex gap-4 text-sm">
            <span className="text-primary-600 font-medium">Tenant</span>
            <Link href="/dashboard/landlord" className="text-gray-500 hover:text-primary-600">Landlord</Link>
            <Link href="/dashboard/investor" className="text-gray-500 hover:text-primary-600">Investor</Link>
          </div>
        </div>
      </nav>

      <div className="max-w-6xl mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-gray-900">🏠 Tenant Dashboard</h1>
          <p className="text-gray-500">Brian Odhiambo — Modern 2BR Apartment, Westlands</p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <div className="card text-center">
            <div className="text-2xl font-bold text-accent-500">
              KES {totalPaid.toLocaleString()}
            </div>
            <div className="text-gray-500 text-sm">Total Paid</div>
          </div>
          <div className="card text-center">
            <div className="text-2xl font-bold text-primary-600">
              KES {totalDue.toLocaleString()}
            </div>
            <div className="text-gray-500 text-sm">Total Due</div>
          </div>
          <div className="card text-center">
            <div className={`text-2xl font-bold ${totalBalance > 0 ? "text-red-500" : "text-accent-500"}`}>
              KES {totalBalance.toLocaleString()}
            </div>
            <div className="text-gray-500 text-sm">Outstanding</div>
          </div>
          <div className="card text-center">
            <div className="text-2xl font-bold text-amber-500">
              {payments.filter(p => p.status === "completed").length}
            </div>
            <div className="text-gray-500 text-sm">Payments Made</div>
          </div>
        </div>

        <div className="grid md:grid-cols-2 gap-8">
          {/* Rent Ledger */}
          <div>
            <h2 className="text-lg font-bold text-gray-900 mb-4">Rent Ledger</h2>
            {loading ? (
              <div className="card animate-pulse h-48" />
            ) : (
              <div className="space-y-3">
                {ledger.map((entry) => (
                  <div key={entry.id} className="card">
                    <div className="flex items-center justify-between mb-2">
                      <div>
                        <div className="font-semibold text-gray-900">{entry.month_year}</div>
                        <div className="text-xs text-gray-500">
                          Due: {new Date(entry.due_date).toLocaleDateString()}
                        </div>
                      </div>
                      <span className={`text-xs px-2 py-1 rounded-full font-medium ${STATUS_COLORS[entry.status] || "bg-gray-100 text-gray-600"}`}>
                        {entry.status.toUpperCase()}
                      </span>
                    </div>
                    <div className="grid grid-cols-3 gap-2 text-sm">
                      <div className="text-center">
                        <div className="font-bold">KES {entry.amount_due.toLocaleString()}</div>
                        <div className="text-xs text-gray-400">Due</div>
                      </div>
                      <div className="text-center">
                        <div className="font-bold text-accent-500">KES {entry.amount_paid.toLocaleString()}</div>
                        <div className="text-xs text-gray-400">Paid</div>
                      </div>
                      <div className="text-center">
                        <div className={`font-bold ${entry.balance > 0 ? "text-red-500" : "text-accent-500"}`}>
                          KES {entry.balance.toLocaleString()}
                        </div>
                        <div className="text-xs text-gray-400">Balance</div>
                      </div>
                    </div>
                    {entry.balance > 0 && (
                      <button className="btn-primary w-full text-sm mt-3">
                        💳 Pay KES {entry.balance.toLocaleString()} via M-Pesa
                      </button>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Payment History */}
          <div>
            <h2 className="text-lg font-bold text-gray-900 mb-4">Payment History</h2>
            {loading ? (
              <div className="card animate-pulse h-48" />
            ) : payments.length === 0 ? (
              <div className="card text-center text-gray-400 py-8">
                <div className="text-3xl mb-2">💳</div>
                <p>No payments yet</p>
              </div>
            ) : (
              <div className="space-y-3">
                {payments.map((payment) => (
                  <div key={payment.id} className="card">
                    <div className="flex items-start justify-between mb-2">
                      <div>
                        <div className="font-semibold text-gray-900 text-sm">
                          {payment.description}
                        </div>
                        <div className="text-xs text-gray-500">
                          {payment.paid_at ? new Date(payment.paid_at).toLocaleString() : "Pending"}
                        </div>
                      </div>
                      <span className={`text-xs px-2 py-1 rounded-full font-medium ${
                        payment.status === "completed" ? "bg-green-100 text-green-700" :
                        payment.status === "pending" ? "bg-yellow-100 text-yellow-700" :
                        "bg-red-100 text-red-700"
                      }`}>
                        {payment.status}
                      </span>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <div>
                        <span className="font-bold text-primary-600">
                          {payment.currency} {payment.amount.toLocaleString()}
                        </span>
                        <span className="text-gray-400 ml-2 uppercase text-xs">
                          via {payment.payment_method}
                        </span>
                      </div>
                      {payment.mpesa_receipt_number && (
                        <span className="text-xs text-gray-400 font-mono">
                          {payment.mpesa_receipt_number}
                        </span>
                      )}
                    </div>
                    {payment.reference_code && (
                      <div className="text-xs text-gray-400 mt-1">
                        Ref: {payment.reference_code}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
