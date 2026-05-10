"use client";
import { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { api } from "@/lib/api";

interface Property {
  id: string;
  title: string;
  description: string;
  price: number;
  currency: string;
  price_period: string;
  bedrooms: number;
  bathrooms: number;
  floor_area_sqm: number;
  city: string;
  neighbourhood: string;
  country: string;
  property_type: string;
  furnishing: string;
  verification_status: string;
  is_featured: boolean;
  view_count: number;
  latitude: number;
  longitude: number;
  images: Array<{ url: string; is_primary: boolean }>;
  amenities: Array<{ amenity: string }>;
}

interface Valuation {
  estimated_value: number;
  confidence_low: number;
  confidence_high: number;
  currency: string;
}

export default function PropertyPage() {
  const params = useParams();
  const id = params.id as string;
  const [property, setProperty] = useState<Property | null>(null);
  const [valuation, setValuation] = useState<Valuation | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!id) return;
    api.getProperty(id)
      .then((data) => {
        setProperty(data);
        return api.getValuation({
          bedrooms: data.bedrooms,
          bathrooms: data.bathrooms,
          floor_area_sqm: data.floor_area_sqm || 60,
          property_type: data.property_type,
          furnishing: data.furnishing,
          price_period: data.price_period,
          city: data.city,
          neighbourhood: data.neighbourhood,
          tier: 2,
          listing_month: new Date().getMonth() + 1,
        });
      })
      .then(setValuation)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <div className="text-4xl mb-4">🏠</div>
        <p className="text-gray-500">Loading property details...</p>
      </div>
    </div>
  );

  if (!property) return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <div className="text-4xl mb-4">😔</div>
        <p className="text-gray-500">Property not found</p>
        <Link href="/" className="btn-primary mt-4 inline-block">Go Home</Link>
      </div>
    </div>
  );

  const isVerified = property.verification_status === "verified";

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navbar */}
      <nav className="bg-white border-b sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
          <Link href="/" className="text-xl font-bold text-primary-600">🏘 AfriProp</Link>
          <Link href="/" className="text-gray-500 hover:text-primary-600">← Back to listings</Link>
        </div>
      </nav>

      <div className="max-w-6xl mx-auto px-4 py-8">
        <div className="grid md:grid-cols-3 gap-8">
          {/* Left — Images + Details */}
          <div className="md:col-span-2">
            {/* Image */}
            <div className="h-72 bg-gradient-to-br from-primary-50 to-primary-100 rounded-2xl mb-6 flex items-center justify-center overflow-hidden relative">
              {property.images?.[0] ? (
                <img src={property.images[0].url} alt={property.title}
                  className="w-full h-full object-cover" />
              ) : (
                <div className="text-6xl">🏠</div>
              )}
              {isVerified && (
                <span className="absolute top-4 right-4 badge-verified text-sm px-3 py-1">
                  ✓ Verified Listing
                </span>
              )}
            </div>

            {/* Title + Price */}
            <div className="card mb-6">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h1 className="text-2xl font-bold text-gray-900 mb-1">{property.title}</h1>
                  <p className="text-gray-500">📍 {property.neighbourhood}, {property.city}, {property.country}</p>
                </div>
                <div className="text-right">
                  <div className="text-3xl font-bold text-primary-600">
                    {property.currency} {property.price.toLocaleString()}
                  </div>
                  <div className="text-gray-400 text-sm">
                    per {property.price_period === "monthly" ? "month" :
                         property.price_period === "yearly" ? "year" : "one-time"}
                  </div>
                </div>
              </div>

              <div className="flex gap-4 text-sm text-gray-600 py-4 border-t border-b border-gray-100 mb-4">
                <span className="flex items-center gap-1">🛏 {property.bedrooms} Bedrooms</span>
                <span className="flex items-center gap-1">🚿 {property.bathrooms} Bathrooms</span>
                {property.floor_area_sqm > 0 && (
                  <span className="flex items-center gap-1">📐 {property.floor_area_sqm}m²</span>
                )}
                <span className="flex items-center gap-1">🛋 {property.furnishing.replace("_", " ")}</span>
              </div>

              <p className="text-gray-600 leading-relaxed">{property.description}</p>
            </div>

            {/* Amenities */}
            {property.amenities?.length > 0 && (
              <div className="card mb-6">
                <h2 className="font-bold text-gray-900 mb-4">Amenities</h2>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                  {property.amenities.map((a, i) => (
                    <div key={i} className="flex items-center gap-2 text-sm text-gray-600">
                      <span className="text-accent-500">✓</span>
                      <span className="capitalize">{a.amenity.replace("_", " ")}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Right — AI Valuation + Actions */}
          <div className="space-y-4">
            {/* AI Valuation Card */}
            {valuation && (
              <div className="card border-l-4 border-primary-500">
                <div className="flex items-center gap-2 mb-3">
                  <span className="text-xl">🤖</span>
                  <h3 className="font-bold text-gray-900">AI Valuation</h3>
                </div>
                <div className="text-2xl font-bold text-primary-600 mb-1">
                  {valuation.currency} {valuation.estimated_value.toLocaleString()}
                </div>
                <div className="text-sm text-gray-500 mb-3">Estimated market value</div>
                <div className="bg-gray-50 rounded-lg p-3 text-sm">
                  <div className="flex justify-between text-gray-600">
                    <span>Low estimate</span>
                    <span className="font-medium">{valuation.currency} {valuation.confidence_low.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between text-gray-600 mt-1">
                    <span>High estimate</span>
                    <span className="font-medium">{valuation.currency} {valuation.confidence_high.toLocaleString()}</span>
                  </div>
                </div>
                <p className="text-xs text-gray-400 mt-2">
                  95% confidence interval • XGBoost model trained on 50K+ African properties
                </p>
              </div>
            )}

            {/* Contact / Actions */}
            <div className="card">
              <h3 className="font-bold text-gray-900 mb-4">Interested in this property?</h3>
              <div className="space-y-3">
                <button className="btn-primary w-full">📞 Contact Landlord</button>
                <button className="btn-secondary w-full">📅 Schedule Viewing</button>
                <button className="btn-secondary w-full">💰 Pay Rent (M-Pesa)</button>
              </div>
              <div className="mt-4 pt-4 border-t border-gray-100 text-center text-sm text-gray-400">
                <p>👁 {property.view_count} people viewed this</p>
              </div>
            </div>

            {/* Property Stats */}
            <div className="card">
              <h3 className="font-bold text-gray-900 mb-3">Property Info</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-500">Type</span>
                  <span className="font-medium capitalize">{property.property_type}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Status</span>
                  <span className="font-medium text-accent-500">Available</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Verification</span>
                  <span className={`font-medium ${isVerified ? "text-accent-500" : "text-yellow-500"}`}>
                    {isVerified ? "✓ Verified" : "Pending"}
                  </span>
                </div>
                {property.latitude && (
                  <div className="flex justify-between">
                    <span className="text-gray-500">Location</span>
                    <span className="font-medium text-xs">
                      {property.latitude.toFixed(4)}, {property.longitude.toFixed(4)}
                    </span>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
