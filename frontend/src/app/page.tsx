"use client";
import { useQuery } from "@tanstack/react-query";
import { getDashboardStats, getAlertEvents, searchPrices } from "@/lib/api";
import { PageHeader } from "@/components/layout/PageHeader";
import { Package, Bell, Activity, TrendingUp } from "lucide-react";
import { formatDistanceToNow } from "date-fns";
import { PLATFORM_LABELS, PLATFORM_COLORS } from "@/lib/types";

function StatCard({ label, value, icon: Icon, color }: { label: string; value: string | number; icon: any; color: string }) {
  return (
    <div className="card p-5">
      <div className="flex items-center justify-between mb-3">
        <span className="text-sm text-gray-500 font-medium">{label}</span>
        <div className={`w-9 h-9 rounded-lg flex items-center justify-center ${color}`}>
          <Icon className="w-4.5 h-4.5 text-white w-5 h-5" />
        </div>
      </div>
      <p className="text-2xl font-bold text-gray-900">{value}</p>
    </div>
  );
}

function PlatformBadge({ platform }: { platform: string }) {
  const color = PLATFORM_COLORS[platform] ?? "#6b7280";
  const label = PLATFORM_LABELS[platform] ?? platform;
  return (
    <span
      className="text-xs font-semibold px-2 py-0.5 rounded-full text-white"
      style={{ backgroundColor: color }}
    >
      {label}
    </span>
  );
}

export default function DashboardPage() {
  const { data: stats } = useQuery({ queryKey: ["dashboard"], queryFn: getDashboardStats });
  const { data: events } = useQuery({ queryKey: ["alert-events"], queryFn: () => getAlertEvents(10) });

  // Quick live demo search to populate the "latest prices" section
  const { data: liveSearch } = useQuery({
    queryKey: ["live-demo"],
    queryFn: () => searchPrices("samsung galaxy", undefined, 6),
    staleTime: 60_000,
  });

  return (
    <div>
      <PageHeader
        title="Dashboard"
        subtitle="Overview of your pricing intelligence"
      />

      <div className="px-6 space-y-6 pb-8">
        {/* Stats */}
        <div className="grid grid-cols-2 xl:grid-cols-4 gap-4">
          <StatCard label="Products Tracked" value={stats?.total_products_tracked ?? 0} icon={Package} color="bg-brand-600" />
          <StatCard label="Price Checks (24h)" value={stats?.price_checks_last_24h ?? 0} icon={Activity} color="bg-emerald-500" />
          <StatCard label="Platforms Active" value={stats?.platforms_active ?? 5} icon={TrendingUp} color="bg-amber-500" />
          <StatCard label="Avg Tracked Price" value={stats ? `MYR ${stats.avg_tracked_price_myr.toFixed(2)}` : "—"} icon={TrendingUp} color="bg-violet-500" />
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-3 gap-5">
          {/* Live Price Sample */}
          <div className="xl:col-span-2 card">
            <div className="px-5 py-4 border-b flex items-center justify-between">
              <h2 className="font-semibold text-gray-800">Live Price Sample</h2>
              <span className="text-xs text-gray-400">Samsung Galaxy · real-time</span>
            </div>
            <div className="divide-y">
              {liveSearch?.results.slice(0, 6).map((r, i) => (
                <div key={i} className="px-5 py-3 flex items-center gap-3">
                  <PlatformBadge platform={r.platform} />
                  <span className="flex-1 text-sm text-gray-700 truncate">{r.title}</span>
                  <div className="text-right shrink-0">
                    <p className="font-semibold text-gray-900 text-sm">MYR {r.price.toFixed(2)}</p>
                    {r.discount_pct && (
                      <p className="text-xs text-emerald-600">-{r.discount_pct}%</p>
                    )}
                  </div>
                </div>
              ))}
              {!liveSearch && (
                <div className="px-5 py-8 text-center text-sm text-gray-400">
                  Loading live prices…
                </div>
              )}
            </div>
          </div>

          {/* Recent Alert Events */}
          <div className="card">
            <div className="px-5 py-4 border-b">
              <h2 className="font-semibold text-gray-800 flex items-center gap-2">
                <Bell className="w-4 h-4 text-amber-500" />
                Recent Alerts
              </h2>
            </div>
            <div className="divide-y">
              {events?.length === 0 && (
                <p className="px-5 py-6 text-sm text-gray-400 text-center">No alerts fired yet</p>
              )}
              {events?.map((e) => (
                <div key={e.id} className="px-4 py-3">
                  <p className="text-sm text-gray-700">{e.message}</p>
                  <p className="text-xs text-gray-400 mt-0.5">
                    {formatDistanceToNow(new Date(e.fired_at), { addSuffix: true })}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Platform Coverage */}
        <div className="card p-5">
          <h2 className="font-semibold text-gray-800 mb-4">Platform Coverage</h2>
          <div className="flex flex-wrap gap-2">
            {Object.entries(PLATFORM_LABELS).map(([key, label]) => (
              <span
                key={key}
                className="px-3 py-1.5 rounded-full text-sm font-medium text-white"
                style={{ backgroundColor: PLATFORM_COLORS[key] ?? "#6b7280" }}
              >
                {label}
              </span>
            ))}
          </div>
          <p className="text-xs text-gray-400 mt-3">
            Real-time price tracking across 5 Malaysian platforms. More coming soon.
          </p>
        </div>
      </div>
    </div>
  );
}
