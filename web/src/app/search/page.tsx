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

interface SearchResult {
  total: number;
  page: number;
  limit: number;
  results: Property[];
}

const CITIES = ["", "Nairobi", "Mombasa", "Lagos", "Accra", "Kampala", "Dar es Salaam"];
const PROPERTY_TYPES = ["", "apartment", "house", "bedsitter", "commercial", "land"];
const SORT_OPTIONS = [
  { value: "newest", label: "Newest First" },
  { value: "price_asc", label: "Price: Low to High" },
  { value: "price_desc", label: "Price: High to Low" },
  { value: "most_viewed", label: "Most Viewed" },
];

function PropertyCard({ property }: { property: Property }) {
  const isVerified = property.verification_status === "verified";
  return (
    <Link href={`/property/${property.id}`}>
      <div className="card hover:shadow-md transition-shadow cursor-pointer flex gap-4">
        <div className="w-48 h-36 bg-gradient-to-br from-primary-50 to-primary-100 rounded-lg flex-shrink-0 flex items-center justify-center overflow-hidden relative">
          {property.images?.[0] ? (
            <img src={property.images[0].url} alt={property.title}
              className="w-full h-full object-cover" />
          ) : (
            <div className="text-3xl">🏠</div>
          )}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between mb-1">
            <h3 className="font-semibold text-gray-900 line-clamp-1">{property.title}</h3>
            <div className="flex gap-1 ml-2 flex-shrink-0">
              {isVerified && <span className="badge-verified text-xs">✓</span>}
              {property.is_featured && (
                <span className="bg-amber-500 text-white text-xs px-2 py-0.5 rounded-full">Featured</span>
              )}
            </div>
          </div>
          <p className="text-gray-500 text-sm mb-2">📍 {property.neighbourhood}, {property.city}</p>
          <div className="flex items-center gap-3 text-sm text-gray-500 mb-3">
            <span>🛏 {property.bedrooms}BR</span>
            <span>🚿 {property.bathrooms}BA</span>
            {property.floor_area_sqm > 0 && <span>📐 {property.floor_area_sqm}m²</span>}
            <span className="capitalize">🛋 {property.furnishing.replace("_"," ")}</span>
          </div>
          <div className="flex items-center justify-between">
            <div>
              <span className="text-lg font-bold text-primary-600">
                {property.currency} {property.price.toLocaleString()}
              </span>
              <span className="text-gray-400 text-sm">
                /{property.price_period === "monthly" ? "mo" :
                  property.price_period === "yearly" ? "yr" : ""}
              </span>
            </div>
            <div className="flex gap-1 flex-wrap">
              {property.amenities?.slice(0, 3).map((a, i) => (
                <span key={i} className="bg-gray-100 text-gray-600 text-xs px-2 py-0.5 rounded-full capitalize">
                  {a.amenity}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>
    </Link>
  );
}

export default function SearchPage() {
  const [filters, setFilters] = useState({
    q: "", city: "", property_type: "",
    min_bedrooms: "", max_price: "",
    sort: "newest", verified: false,
  });
  const [results, setResults] = useState<SearchResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(1);

  const search = async (p = 1) => {
    setLoading(true);
    try {
      const params: Record<string, string | number> = { limit: 10, page: p };
      if (filters.q)            params.q             = filters.q;
      if (filters.city)         params.city          = filters.city;
      if (filters.property_type)params.property_type = filters.property_type;
      if (filters.min_bedrooms) params.min_bedrooms  = filters.min_bedrooms;
      if (filters.max_price)    params.max_price     = filters.max_price;
      if (filters.verified)     params.verified      = "true";
      params.sort = filters.sort;
      const data = await api.searchProperties(params);
      setResults(data);
      setPage(p);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { search(1); }, []);

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white border-b sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
          <Link href="/" className="text-xl font-bold text-primary-600">🏘 AfriProp</Link>
          <div className="flex-1 max-w-md mx-4">
            <input
              type="text"
              placeholder="Search properties..."
              value={filters.q}
              onChange={(e) => setFilters({...filters, q: e.target.value})}
              onKeyDown={(e) => e.key === "Enter" && search(1)}
              className="input text-sm"
            />
          </div>
          <button onClick={() => search(1)} className="btn-primary text-sm">Search</button>
        </div>
      </nav>

      <div className="max-w-6xl mx-auto px-4 py-6">
        <div className="grid md:grid-cols-4 gap-6">
          {/* Filters Sidebar */}
          <div className="md:col-span-1">
            <div className="card sticky top-20">
              <h2 className="font-bold text-gray-900 mb-4">Filters</h2>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">City</label>
                  <select className="input text-sm" value={filters.city}
                    onChange={(e) => setFilters({...filters, city: e.target.value})}>
                    <option value="">All Cities</option>
                    {CITIES.filter(Boolean).map((c) => <option key={c} value={c}>{c}</option>)}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Property Type</label>
                  <select className="input text-sm" value={filters.property_type}
                    onChange={(e) => setFilters({...filters, property_type: e.target.value})}>
                    <option value="">All Types</option>
                    {PROPERTY_TYPES.filter(Boolean).map((t) => (
                      <option key={t} value={t} className="capitalize">{t}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Min Bedrooms</label>
                  <select className="input text-sm" value={filters.min_bedrooms}
                    onChange={(e) => setFilters({...filters, min_bedrooms: e.target.value})}>
                    <option value="">Any</option>
                    {[1,2,3,4,5].map((n) => <option key={n} value={n}>{n}+</option>)}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Max Price</label>
                  <input type="number" placeholder="e.g. 100000" className="input text-sm"
                    value={filters.max_price}
                    onChange={(e) => setFilters({...filters, max_price: e.target.value})} />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Sort By</label>
                  <select className="input text-sm" value={filters.sort}
                    onChange={(e) => setFilters({...filters, sort: e.target.value})}>
                    {SORT_OPTIONS.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
                  </select>
                </div>

                <div className="flex items-center gap-2">
                  <input type="checkbox" id="verified" checked={filters.verified}
                    onChange={(e) => setFilters({...filters, verified: e.target.checked})}
                    className="rounded" />
                  <label htmlFor="verified" className="text-sm text-gray-700">Verified only</label>
                </div>

                <button onClick={() => search(1)} className="btn-primary w-full text-sm">
                  Apply Filters
                </button>

                <button
                  onClick={() => {
                    setFilters({ q:"", city:"", property_type:"", min_bedrooms:"",
                      max_price:"", sort:"newest", verified:false });
                  }}
                  className="btn-secondary w-full text-sm"
                >
                  Clear Filters
                </button>
              </div>
            </div>
          </div>

          {/* Results */}
          <div className="md:col-span-3">
            <div className="flex items-center justify-between mb-4">
              <h1 className="text-lg font-bold text-gray-900">
                {loading ? "Searching..." :
                  results ? `${results.total} properties found` : "Search Properties"}
              </h1>
            </div>

            {loading ? (
              <div className="space-y-4">
                {[1,2,3,4].map((i) => (
                  <div key={i} className="card animate-pulse flex gap-4">
                    <div className="w-48 h-36 bg-gray-100 rounded-lg flex-shrink-0" />
                    <div className="flex-1 space-y-3">
                      <div className="h-4 bg-gray-100 rounded w-3/4" />
                      <div className="h-4 bg-gray-100 rounded w-1/2" />
                      <div className="h-4 bg-gray-100 rounded w-1/4" />
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="space-y-4">
                {results?.results.map((p) => (
                  <PropertyCard key={p.id} property={p} />
                ))}
                {results?.results.length === 0 && (
                  <div className="text-center py-12 text-gray-400">
                    <div className="text-4xl mb-4">🔍</div>
                    <p>No properties found matching your filters.</p>
                    <p className="text-sm mt-1">Try adjusting your search criteria.</p>
                  </div>
                )}
              </div>
            )}

            {/* Pagination */}
            {results && results.total > 10 && (
              <div className="flex items-center justify-center gap-2 mt-6">
                <button
                  onClick={() => search(page - 1)}
                  disabled={page === 1}
                  className="btn-secondary text-sm disabled:opacity-50"
                >
                  ← Previous
                </button>
                <span className="text-sm text-gray-500">
                  Page {page} of {Math.ceil(results.total / 10)}
                </span>
                <button
                  onClick={() => search(page + 1)}
                  disabled={page >= Math.ceil(results.total / 10)}
                  className="btn-secondary text-sm disabled:opacity-50"
                >
                  Next →
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
