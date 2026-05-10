"use client";
import { useState, useEffect } from "react";
import Link from "next/link";
import { api } from "@/lib/api";

interface Property {
  id: string;
  title: string;
  price: number;
  currency: string;
  price_period: string;
  bedrooms: number;
  bathrooms: number;
  floor_area_sqm: number;
  city: string;
  neighbourhood: string;
  property_type: string;
  furnishing: string;
  verification_status: string;
  is_featured: boolean;
  view_count: number;
  images: Array<{ url: string; is_primary: boolean }>;
  amenities: Array<{ amenity: string }>;
}

function PropertyCard({ property }: { property: Property }) {
  const isVerified = property.verification_status === "verified";
  return (
    <Link href={`/property/${property.id}`}>
      <div className="card hover:shadow-md transition-shadow cursor-pointer">
        <div className="h-48 bg-gradient-to-br from-primary-50 to-primary-100 rounded-lg mb-4 flex items-center justify-center relative overflow-hidden">
          {property.images?.[0] ? (
            <img
              src={property.images[0].url}
              alt={property.title}
              className="w-full h-full object-cover rounded-lg"
            />
          ) : (
            <div className="text-primary-600 text-4xl">🏠</div>
          )}
          {isVerified && (
            <span className="absolute top-2 right-2 badge-verified">✓ Verified</span>
          )}
          {property.is_featured && (
            <span className="absolute top-2 left-2 bg-amber-500 text-white text-xs px-2 py-1 rounded-full font-medium">
              Featured
            </span>
          )}
        </div>
        <h3 className="font-semibold text-gray-900 mb-1 line-clamp-1">{property.title}</h3>
        <p className="text-gray-500 text-sm mb-2">
          📍 {property.neighbourhood}, {property.city}
        </p>
        <div className="flex items-center gap-2 text-sm text-gray-500 mb-3">
          <span>🛏 {property.bedrooms}BR</span>
          <span>🚿 {property.bathrooms}BA</span>
          {property.floor_area_sqm > 0 && <span>📐 {property.floor_area_sqm}m²</span>}
        </div>
        <div className="flex items-center justify-between">
          <div>
            <span className="text-xl font-bold text-primary-600">
              {property.currency} {property.price.toLocaleString()}
            </span>
            <span className="text-gray-400 text-sm">
              /{property.price_period === "monthly" ? "mo" : property.price_period === "yearly" ? "yr" : ""}
            </span>
          </div>
          <span className="text-xs text-gray-400">{property.view_count} views</span>
        </div>
      </div>
    </Link>
  );
}

function HeroSearch({ onSearch }: { onSearch: (q: string, city: string) => void }) {
  const [query, setQuery] = useState("");
  const [city, setCity] = useState("");

  return (
    <div className="bg-gradient-to-br from-primary-600 to-primary-900 text-white py-20 px-4">
      <div className="max-w-4xl mx-auto text-center">
        <h1 className="text-4xl md:text-5xl font-bold mb-4">
          Find Your Perfect Property in Africa
        </h1>
        <p className="text-primary-100 text-lg mb-8">
          AI-powered property intelligence across 6 African cities.
          Search, verify, invest — all in one platform.
        </p>
        <div className="bg-white rounded-2xl p-2 flex flex-col md:flex-row gap-2 shadow-xl">
          <input
            type="text"
            placeholder="Search by neighbourhood, type..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="flex-1 input border-0 focus:ring-0 text-gray-900"
          />
          <select
            value={city}
            onChange={(e) => setCity(e.target.value)}
            className="input border-0 focus:ring-0 text-gray-900 md:w-48"
          >
            <option value="">All Cities</option>
            <option value="Nairobi">Nairobi</option>
            <option value="Mombasa">Mombasa</option>
            <option value="Lagos">Lagos</option>
            <option value="Accra">Accra</option>
            <option value="Kampala">Kampala</option>
            <option value="Dar es Salaam">Dar es Salaam</option>
          </select>
          <button
            onClick={() => onSearch(query, city)}
            className="btn-primary md:px-8"
          >
            🔍 Search
          </button>
        </div>
        <div className="flex justify-center gap-8 mt-8 text-primary-100 text-sm">
          <span>📱 SMS: HOUSE 2BR NAIROBI</span>
          <span>📞 Dial: *384*PROP#</span>
          <span>🤖 AI Valuation</span>
        </div>
      </div>
    </div>
  );
}

function StatsBar() {
  return (
    <div className="bg-white border-b">
      <div className="max-w-6xl mx-auto px-4 py-4 grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
        <div>
          <div className="text-2xl font-bold text-primary-600">6</div>
          <div className="text-gray-500 text-sm">African Cities</div>
        </div>
        <div>
          <div className="text-2xl font-bold text-primary-600">50K+</div>
          <div className="text-gray-500 text-sm">Properties Analysed</div>
        </div>
        <div>
          <div className="text-2xl font-bold text-primary-600">AI</div>
          <div className="text-gray-500 text-sm">Powered Valuation</div>
        </div>
        <div>
          <div className="text-2xl font-bold text-primary-600">M-Pesa</div>
          <div className="text-gray-500 text-sm">Rent Payments</div>
        </div>
      </div>
    </div>
  );
}

export default function Home() {
  const [properties, setProperties] = useState<Property[]>([]);
  const [loading, setLoading] = useState(true);
  const [city, setCity] = useState("Nairobi");

  const loadProperties = async (q = "", selectedCity = "Nairobi") => {
    setLoading(true);
    try {
      const params: Record<string, string | number> = { limit: 6 };
      if (selectedCity) params.city = selectedCity;
      if (q) params.q = q;
      const data = await api.searchProperties(params);
      setProperties(data.results || []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadProperties("", city); }, [city]);

  const handleSearch = (q: string, selectedCity: string) => {
    setCity(selectedCity);
    loadProperties(q, selectedCity);
  };

  return (
    <div>
      {/* Navbar */}
      <nav className="bg-white border-b sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
          <Link href="/" className="text-xl font-bold text-primary-600">
            🏘 AfriProp
          </Link>
          <div className="hidden md:flex items-center gap-6 text-sm text-gray-600">
            <Link href="/search" className="hover:text-primary-600">Search</Link>
            <Link href="/mortgage" className="hover:text-primary-600">Mortgage</Link>
            <Link href="/dashboard/investor" className="hover:text-primary-600">Invest</Link>
          </div>
          <div className="flex gap-2">
            <Link href="/auth/login" className="btn-secondary text-sm">Login</Link>
            <Link href="/auth/register" className="btn-primary text-sm">List Property</Link>
          </div>
        </div>
      </nav>

      <HeroSearch onSearch={handleSearch} />
      <StatsBar />

      {/* Featured Properties */}
      <div className="max-w-6xl mx-auto px-4 py-12">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-gray-900">
            Properties in {city || "Africa"}
          </h2>
          <div className="flex gap-2">
            {["Nairobi","Mombasa","Lagos","Accra"].map((c) => (
              <button
                key={c}
                onClick={() => { setCity(c); loadProperties("", c); }}
                className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                  city === c
                    ? "bg-primary-600 text-white"
                    : "bg-gray-100 text-gray-600 hover:bg-gray-200"
                }`}
              >
                {c}
              </button>
            ))}
          </div>
        </div>

        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[1,2,3,4,5,6].map((i) => (
              <div key={i} className="card animate-pulse">
                <div className="h-48 bg-gray-100 rounded-lg mb-4" />
                <div className="h-4 bg-gray-100 rounded mb-2" />
                <div className="h-4 bg-gray-100 rounded w-2/3" />
              </div>
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {properties.map((p) => (
              <PropertyCard key={p.id} property={p} />
            ))}
          </div>
        )}

        {!loading && properties.length === 0 && (
          <div className="text-center py-12 text-gray-400">
            <div className="text-4xl mb-4">🏠</div>
            <p>No properties found. Try a different city or search term.</p>
          </div>
        )}

        <div className="text-center mt-8">
          <Link href="/search" className="btn-secondary">
            View All Properties →
          </Link>
        </div>
      </div>

      {/* AI Features Banner */}
      <div className="bg-gradient-to-r from-accent-600 to-primary-600 text-white py-12">
        <div className="max-w-6xl mx-auto px-4 grid md:grid-cols-3 gap-8 text-center">
          <div>
            <div className="text-3xl mb-3">🤖</div>
            <h3 className="font-bold text-lg mb-2">AI Property Valuation</h3>
            <p className="text-green-100 text-sm">
              Get instant AI-estimated market value with 95% confidence intervals.
              Powered by XGBoost trained on 50,000+ African properties.
            </p>
            <Link href="/mortgage" className="mt-4 inline-block bg-white text-primary-600 px-4 py-2 rounded-lg text-sm font-medium">
              Try Valuation →
            </Link>
          </div>
          <div>
            <div className="text-3xl mb-3">📱</div>
            <h3 className="font-bold text-lg mb-2">Works on Any Phone</h3>
            <p className="text-green-100 text-sm">
              No smartphone needed. Search properties via SMS or USSD.
              Dial *384*PROP# or text HOUSE 2BR NAIROBI to our shortcode.
            </p>
          </div>
          <div>
            <div className="text-3xl mb-3">💰</div>
            <h3 className="font-bold text-lg mb-2">Fractional Investment</h3>
            <p className="text-green-100 text-sm">
              Own a piece of premium African real estate from KES 5,000.
              Earn monthly rental income proportional to your ownership.
            </p>
            <Link href="/dashboard/investor" className="mt-4 inline-block bg-white text-primary-600 px-4 py-2 rounded-lg text-sm font-medium">
              Start Investing →
            </Link>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-gray-900 text-gray-400 py-8">
        <div className="max-w-6xl mx-auto px-4 text-center">
          <div className="text-white font-bold text-lg mb-2">🏘 AfriProp</div>
          <p className="text-sm mb-4">
            Property Intelligence Platform for Africa
          </p>
          <div className="flex justify-center gap-6 text-sm">
            <span>SMS: HOUSE 2BR NAIROBI</span>
            <span>USSD: *384*PROP#</span>
            <span>Built for the Real Estate Solutions Hackathon</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
