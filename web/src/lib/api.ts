const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function fetchAPI(path: string, options?: RequestInit) {
  const res = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export const api = {
  searchProperties: (params: Record<string, string | number>) => {
    const query = new URLSearchParams(
      Object.entries(params).reduce((acc, [k, v]) => ({...acc, [k]: String(v)}), {})
    ).toString();
    return fetchAPI(`/api/v1/properties/?${query}`);
  },
  getProperty: (id: string) => fetchAPI(`/api/v1/properties/${id}`),
  nearbyProperties: (lat: number, lng: number, radius = 5) =>
    fetchAPI(`/api/v1/properties/nearby?lat=${lat}&lng=${lng}&radius_km=${radius}`),
  getValuation: (data: Record<string, unknown>) =>
    fetchAPI("/api/v1/ml/valuation", { method: "POST", body: JSON.stringify(data) }),
  getTrend: (city: string, neighbourhood: string) =>
    fetchAPI("/api/v1/ml/trends", {
      method: "POST",
      body: JSON.stringify({ city, neighbourhood, forecast_months: 6 }),
    }),
  calculateMortgage: (data: Record<string, unknown>) =>
    fetchAPI("/api/v1/finance/mortgage/calculate", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  getInvestments: () => fetchAPI("/api/v1/finance/investments/"),
  login: (phone: string, password: string) =>
    fetchAPI("/api/v1/auth/login", {
      method: "POST",
      body: JSON.stringify({ phone, password }),
    }),
  register: (data: Record<string, unknown>) =>
    fetchAPI("/api/v1/auth/register", {
      method: "POST",
      body: JSON.stringify(data),
    }),
};
