"use client";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { searchPrices, getFairPriceLive } from "@/lib/api";
import { PageHeader } from "@/components/layout/PageHeader";
import { Search, ExternalLink, TrendingDown, Info } from "lucide-react";
import { PLATFORM_LABELS, PLATFORM_COLORS } from "@/lib/types";
import { clsx } from "clsx";

const ALL_PLATFORMS = ["lazada", "shopee", "aeon", "jaya_grocer", "lotus"];

export default function SearchPage() {
  const [query, setQuery] = useState("");
  const [submitted, setSubmitted] = useState("");
  const [selectedPlatforms, setSelectedPlatforms] = useState<string[]>([]);
  const [sortBy, setSortBy] = useState<"price" | "platform">("price");

  const platformsParam = selectedPlatforms.length > 0 ? selectedPlatforms.join(",") : undefined;

  const { data: results, isFetching } = useQuery({
    queryKey: ["search", submitted, platformsParam],
    queryFn: () => searchPrices(submitted, platformsParam, 12),
    enabled: submitted.length > 0,
  });

  const { data: fairPrice } = useQuery({
    queryKey: ["fair-price", submitted, platformsParam],
    queryFn: () => getFairPriceLive(submitted, platformsParam),
    enabled: submitted.length > 0,
  });

  const sorted = [...(results?.results ?? [])].sort((a, b) =>
    sortBy === "price" ? a.price - b.price : a.platform.localeCompare(b.platform)
  );

  function togglePlatform(p: string) {
    setSelectedPlatforms(prev => prev.includes(p) ? prev.filter(x => x !== p) : [...prev, p]);
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (query.trim()) setSubmitted(query.trim());
  }

  function getClassification(price: number) {
    if (!fairPrice) return null;
    if (price <= fairPrice.cheap_threshold) return "Cheap";
    if (price >= fairPrice.expensive_threshold) return "Expensive";
    return "Fair";
  }

  return (
    <div>
      <PageHeader title="Search & Compare" subtitle="Live prices across all Malaysian platforms" />

      <div className="px-6 space-y-5 pb-8">
        {/* Search form */}
        <form onSubmit={handleSubmit} className="flex gap-2">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              value={query}
              onChange={e => setQuery(e.target.value)}
              placeholder="Search any product… e.g. iPhone 15, Milo 1kg, Samsung TV"
              className="w-full pl-9 pr-4 py-2.5 border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
            />
          </div>
          <button type="submit" className="btn-primary">
            {isFetching ? "Searching…" : "Search"}
          </button>
        </form>

        {/* Platform filters */}
        <div className="flex flex-wrap gap-2">
          {ALL_PLATFORMS.map(p => (
            <button
              key={p}
              onClick={() => togglePlatform(p)}
              className={clsx(
                "px-3 py-1 rounded-full text-xs font-medium border transition-all",
                selectedPlatforms.includes(p)
                  ? "text-white border-transparent"
                  : "bg-white text-gray-600 hover:border-gray-400"
              )}
              style={selectedPlatforms.includes(p) ? { backgroundColor: PLATFORM_COLORS[p] } : undefined}
            >
              {PLATFORM_LABELS[p]}
            </button>
          ))}
          {selectedPlatforms.length > 0 && (
            <button onClick={() => setSelectedPlatforms([])} className="px-3 py-1 rounded-full text-xs text-gray-500 border hover:bg-gray-50">
              Clear filters
            </button>
          )}
        </div>

        {/* Fair Price Banner */}
        {fairPrice && (
          <div className="card p-4 bg-gradient-to-r from-brand-50 to-blue-50 border-brand-200">
            <div className="flex items-start gap-3">
              <Info className="w-5 h-5 text-brand-600 mt-0.5 shrink-0" />
              <div className="flex-1">
                <p className="font-semibold text-brand-800 text-sm">Fair Price Intelligence — {fairPrice.product_name}</p>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-2">
                  <div>
                    <p className="text-xs text-gray-500">Market Median</p>
                    <p className="font-bold text-gray-900">MYR {fairPrice.median_price.toFixed(2)}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Fair Range</p>
                    <p className="font-bold text-emerald-700">MYR {fairPrice.fair_price_low.toFixed(2)} – {fairPrice.fair_price_high.toFixed(2)}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Cheapest</p>
                    <p className="font-bold text-gray-900">MYR {fairPrice.min_price.toFixed(2)}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Listings Found</p>
                    <p className="font-bold text-gray-900">{fairPrice.total_listings}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Results */}
        {sorted.length > 0 && (
          <div className="card">
            <div className="px-5 py-3 border-b flex items-center justify-between">
              <p className="text-sm font-medium text-gray-700">
                {results?.total_results} results · {results?.search_duration_ms}ms
              </p>
              <div className="flex gap-1">
                <button onClick={() => setSortBy("price")} className={clsx("px-3 py-1 text-xs rounded-md font-medium", sortBy === "price" ? "bg-brand-600 text-white" : "bg-gray-100 text-gray-600")}>
                  Sort by Price
                </button>
                <button onClick={() => setSortBy("platform")} className={clsx("px-3 py-1 text-xs rounded-md font-medium", sortBy === "platform" ? "bg-brand-600 text-white" : "bg-gray-100 text-gray-600")}>
                  By Platform
                </button>
              </div>
            </div>

            <div className="divide-y">
              {sorted.map((r, i) => {
                const cls = getClassification(r.price);
                return (
                  <div key={i} className="px-5 py-3.5 flex items-center gap-4">
                    {r.image_url ? (
                      <img src={r.image_url} alt="" className="w-12 h-12 object-contain rounded-md border shrink-0" />
                    ) : (
                      <div className="w-12 h-12 bg-gray-100 rounded-md shrink-0" />
                    )}
                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-gray-800 font-medium truncate">{r.title}</p>
                      <div className="flex items-center gap-2 mt-0.5">
                        <span
                          className="text-xs font-semibold px-2 py-0.5 rounded-full text-white"
                          style={{ backgroundColor: PLATFORM_COLORS[r.platform] ?? "#6b7280" }}
                        >
                          {PLATFORM_LABELS[r.platform] ?? r.platform}
                        </span>
                        {r.seller_name && <span className="text-xs text-gray-400">{r.seller_name}</span>}
                        {r.rating && <span className="text-xs text-amber-500">★ {r.rating.toFixed(1)}</span>}
                      </div>
                    </div>
                    <div className="text-right shrink-0">
                      <div className="flex items-center gap-2">
                        {cls && (
                          <span className={clsx(
                            "text-xs font-semibold px-2 py-0.5 rounded-full",
                            cls === "Cheap" ? "badge-cheap" : cls === "Expensive" ? "badge-expensive" : "badge-fair"
                          )}>
                            {cls}
                          </span>
                        )}
                        <p className="font-bold text-gray-900">MYR {r.price.toFixed(2)}</p>
                      </div>
                      {r.original_price && (
                        <p className="text-xs text-gray-400 line-through">MYR {r.original_price.toFixed(2)}</p>
                      )}
                      {r.discount_pct && (
                        <p className="text-xs text-emerald-600 flex items-center gap-0.5 justify-end">
                          <TrendingDown className="w-3 h-3" /> {r.discount_pct}% off
                        </p>
                      )}
                    </div>
                    {r.url && (
                      <a href={r.url} target="_blank" rel="noopener noreferrer" className="shrink-0 text-gray-400 hover:text-brand-600">
                        <ExternalLink className="w-4 h-4" />
                      </a>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {submitted && !isFetching && sorted.length === 0 && (
          <div className="text-center py-12 text-gray-400">
            <Search className="w-10 h-10 mx-auto mb-3 opacity-30" />
            <p>No results found for &ldquo;{submitted}&rdquo;</p>
          </div>
        )}
      </div>
    </div>
  );
}
