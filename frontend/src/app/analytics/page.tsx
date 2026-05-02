"use client";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { getProducts, getProductFairPrice, getProductHistory } from "@/lib/api";
import { PageHeader } from "@/components/layout/PageHeader";
import {
  LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer,
  BarChart, Bar, Legend, ReferenceLine,
} from "recharts";
import { format } from "date-fns";
import { PLATFORM_COLORS, PLATFORM_LABELS } from "@/lib/types";
import type { Product } from "@/lib/types";

export default function AnalyticsPage() {
  const { data: products = [] } = useQuery({ queryKey: ["products"], queryFn: getProducts });
  const [selectedId, setSelectedId] = useState<string>("");
  const productId = selectedId || (products[0] as Product | undefined)?.id || "";

  const { data: fairPrice } = useQuery({
    queryKey: ["fair-price-db", productId],
    queryFn: () => getProductFairPrice(productId),
    enabled: !!productId,
  });

  const { data: history } = useQuery({
    queryKey: ["history", productId],
    queryFn: () => getProductHistory(productId, 30),
    enabled: !!productId,
  });

  const chartData = history?.data_points.map((p: any) => ({
    date: format(new Date(p.captured_at), "MMM d"),
    price: p.price,
    platform: p.platform,
  })) ?? [];

  const platforms = [...new Set(chartData.map((d: any) => d.platform))];

  return (
    <div>
      <PageHeader title="Analytics" subtitle="Price history and market intelligence" />

      <div className="px-6 space-y-6 pb-8">
        {/* Product selector */}
        {products.length > 0 && (
          <select
            value={selectedId}
            onChange={e => setSelectedId(e.target.value)}
            className="border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 bg-white"
          >
            {products.map((p: Product) => (
              <option key={p.id} value={p.id}>{p.name}</option>
            ))}
          </select>
        )}

        {products.length === 0 && (
          <p className="text-sm text-gray-400 py-4">Add products to see analytics.</p>
        )}

        {/* Fair Price Stats */}
        {fairPrice && (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            {[
              { label: "Market Median", value: `MYR ${fairPrice.median_price.toFixed(2)}`, highlight: false },
              { label: "Fair Range", value: `MYR ${fairPrice.fair_price_low.toFixed(2)}–${fairPrice.fair_price_high.toFixed(2)}`, highlight: true },
              { label: "Cheapest", value: `MYR ${fairPrice.min_price.toFixed(2)}`, highlight: false },
              { label: "Most Expensive", value: `MYR ${fairPrice.max_price.toFixed(2)}`, highlight: false },
            ].map(item => (
              <div key={item.label} className={`card p-4 ${item.highlight ? "border-brand-300 bg-brand-50" : ""}`}>
                <p className="text-xs text-gray-500">{item.label}</p>
                <p className={`text-lg font-bold mt-1 ${item.highlight ? "text-brand-700" : "text-gray-900"}`}>{item.value}</p>
              </div>
            ))}
          </div>
        )}

        {/* Price History Chart */}
        {chartData.length > 0 && (
          <div className="card p-5">
            <h2 className="font-semibold text-gray-800 mb-4">Price History (30 days)</h2>
            <ResponsiveContainer width="100%" height={280}>
              <LineChart data={chartData}>
                <XAxis dataKey="date" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} domain={["auto", "auto"]} tickFormatter={v => `RM${v}`} />
                <Tooltip formatter={(v: number) => [`MYR ${v.toFixed(2)}`, "Price"]} />
                <Line type="monotone" dataKey="price" stroke="#6366f1" strokeWidth={2} dot={false} />
                {fairPrice && (
                  <>
                    <ReferenceLine y={fairPrice.fair_price_low} stroke="#10b981" strokeDasharray="4 4" label={{ value: "Fair Low", fontSize: 10 }} />
                    <ReferenceLine y={fairPrice.fair_price_high} stroke="#f59e0b" strokeDasharray="4 4" label={{ value: "Fair High", fontSize: 10 }} />
                  </>
                )}
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Platform distribution */}
        {fairPrice && fairPrice.platforms_covered.length > 1 && (
          <div className="card p-5">
            <h2 className="font-semibold text-gray-800 mb-4">Platform Coverage</h2>
            <div className="flex flex-wrap gap-2">
              {fairPrice.platforms_covered.map(p => (
                <span key={p} className="px-3 py-1.5 rounded-full text-sm font-medium text-white"
                  style={{ backgroundColor: PLATFORM_COLORS[p] ?? "#6b7280" }}>
                  {PLATFORM_LABELS[p] ?? p}
                </span>
              ))}
            </div>
            <p className="text-xs text-gray-400 mt-2">Based on {fairPrice.total_listings} listings</p>
          </div>
        )}
      </div>
    </div>
  );
}
