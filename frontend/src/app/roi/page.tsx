"use client";
import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { simulateROI } from "@/lib/api";
import { PageHeader } from "@/components/layout/PageHeader";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell,
  ReferenceLine, Legend,
} from "recharts";
import { Calculator, TrendingUp, TrendingDown, Info, Zap } from "lucide-react";
import { clsx } from "clsx";
import type { ROIOutput } from "@/lib/types";

export default function ROIPage() {
  const [form, setForm] = useState({
    selling_price: "99.90",
    cost_price: "45.00",
    monthly_units: "100",
    price_elasticity: "-1.5",
    market_median_price: "",
  });

  const mut = useMutation({ mutationFn: simulateROI });
  const result: ROIOutput | undefined = mut.data;

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    mut.mutate({
      selling_price: +form.selling_price,
      cost_price: +form.cost_price,
      monthly_units: +form.monthly_units,
      price_elasticity: +form.price_elasticity,
      market_median_price: form.market_median_price ? +form.market_median_price : undefined,
    });
  }

  const chartData = result?.scenarios.map(s => ({
    price: `RM${s.price.toFixed(0)}`,
    profit: s.gross_profit,
    revenue: s.revenue,
    margin: s.margin_pct,
    isOptimal: s.price === result.optimal_price,
    isCurrent: s.price === result.current.price,
  })) ?? [];

  return (
    <div>
      <PageHeader title="ROI Calculator" subtitle="Simulate profit impact of price changes" />

      <div className="px-6 space-y-6 pb-8">
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
          {/* Input form */}
          <div className="card p-5">
            <h2 className="font-semibold text-gray-800 mb-4 flex items-center gap-2">
              <Calculator className="w-4 h-4 text-brand-600" /> Input Parameters
            </h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="text-sm font-medium text-gray-700">Selling Price (MYR)</label>
                <input type="number" step="0.01" required value={form.selling_price}
                  onChange={e => setForm(p => ({ ...p, selling_price: e.target.value }))}
                  className="mt-1 w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500" />
              </div>
              <div>
                <label className="text-sm font-medium text-gray-700">Cost / COGS per unit (MYR)</label>
                <input type="number" step="0.01" required value={form.cost_price}
                  onChange={e => setForm(p => ({ ...p, cost_price: e.target.value }))}
                  className="mt-1 w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500" />
              </div>
              <div>
                <label className="text-sm font-medium text-gray-700">Monthly Units Sold</label>
                <input type="number" step="1" required value={form.monthly_units}
                  onChange={e => setForm(p => ({ ...p, monthly_units: e.target.value }))}
                  className="mt-1 w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500" />
              </div>
              <div>
                <label className="text-sm font-medium text-gray-700 flex items-center gap-1">
                  Price Elasticity
                  <span title="How sensitive demand is to price. -1.5 is typical. -2 means very price-sensitive." className="cursor-help">
                    <Info className="w-3.5 h-3.5 text-gray-400" />
                  </span>
                </label>
                <input type="number" step="0.1" required value={form.price_elasticity}
                  onChange={e => setForm(p => ({ ...p, price_elasticity: e.target.value }))}
                  className="mt-1 w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500" />
                <p className="text-xs text-gray-400 mt-1">Typical: -1.0 (inelastic) to -2.5 (very elastic)</p>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-700">Market Median Price (optional)</label>
                <input type="number" step="0.01" value={form.market_median_price}
                  onChange={e => setForm(p => ({ ...p, market_median_price: e.target.value }))}
                  placeholder="From Fair Price Engine"
                  className="mt-1 w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500" />
              </div>
              <button type="submit" disabled={mut.isPending} className="btn-primary w-full flex items-center justify-center gap-2">
                <Zap className="w-4 h-4" />
                {mut.isPending ? "Simulating…" : "Run Simulation"}
              </button>
            </form>
          </div>

          {/* Results */}
          <div className="xl:col-span-2 space-y-4">
            {result && (
              <>
                {/* Key metrics */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                  {[
                    { label: "Current Revenue", value: `MYR ${result.current.revenue.toFixed(0)}`, sub: `/mo` },
                    { label: "Current Profit", value: `MYR ${result.current.gross_profit.toFixed(0)}`, sub: `${result.current.margin_pct.toFixed(1)}% margin` },
                    { label: "Optimal Price", value: `MYR ${result.optimal_price.toFixed(2)}`, sub: "max profit", highlight: true },
                    { label: "Break-even", value: `MYR ${result.break_even_price.toFixed(2)}`, sub: "min viable" },
                  ].map(item => (
                    <div key={item.label} className={clsx("card p-4", item.highlight && "border-brand-300 bg-brand-50")}>
                      <p className="text-xs text-gray-500">{item.label}</p>
                      <p className={clsx("text-lg font-bold mt-0.5", item.highlight ? "text-brand-700" : "text-gray-900")}>{item.value}</p>
                      <p className="text-xs text-gray-400">{item.sub}</p>
                    </div>
                  ))}
                </div>

                {/* Recommendation */}
                <div className="card p-4 border-l-4 border-brand-500 bg-brand-50">
                  <p className="text-sm font-medium text-brand-800 flex items-center gap-2">
                    <TrendingUp className="w-4 h-4 shrink-0" /> Recommendation
                  </p>
                  <p className="text-sm text-brand-700 mt-1">{result.recommendation}</p>
                  {result.market_position && (
                    <p className="text-xs text-brand-600 mt-1 opacity-80">{result.market_position}</p>
                  )}
                </div>

                {/* Chart */}
                <div className="card p-5">
                  <h2 className="font-semibold text-gray-800 mb-4">Gross Profit by Price Point</h2>
                  <ResponsiveContainer width="100%" height={260}>
                    <BarChart data={chartData} barSize={20}>
                      <XAxis dataKey="price" tick={{ fontSize: 10 }} />
                      <YAxis tick={{ fontSize: 10 }} tickFormatter={v => `RM${v.toFixed(0)}`} />
                      <Tooltip formatter={(v: number, name: string) => [`MYR ${v.toFixed(2)}`, name === "profit" ? "Gross Profit" : "Revenue"]} />
                      <Bar dataKey="profit" name="Gross Profit" radius={[3, 3, 0, 0]}>
                        {chartData.map((entry, i) => (
                          <Cell
                            key={i}
                            fill={entry.isOptimal ? "#6366f1" : entry.isCurrent ? "#f59e0b" : "#c7d2fe"}
                          />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                  <div className="flex gap-4 mt-2 text-xs text-gray-500">
                    <span><span className="inline-block w-3 h-3 rounded-sm bg-brand-500 mr-1" />Optimal price</span>
                    <span><span className="inline-block w-3 h-3 rounded-sm bg-amber-400 mr-1" />Current price</span>
                    <span><span className="inline-block w-3 h-3 rounded-sm bg-brand-200 mr-1" />Other scenarios</span>
                  </div>
                </div>

                {/* Scenario table */}
                <div className="card overflow-hidden">
                  <div className="px-5 py-3 border-b bg-gray-50">
                    <h2 className="text-sm font-semibold text-gray-700">All Price Scenarios</h2>
                  </div>
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b text-xs text-gray-500">
                          <th className="px-4 py-2 text-left">Price</th>
                          <th className="px-4 py-2 text-right">Units/mo</th>
                          <th className="px-4 py-2 text-right">Revenue</th>
                          <th className="px-4 py-2 text-right">Profit</th>
                          <th className="px-4 py-2 text-right">Margin</th>
                          <th className="px-4 py-2 text-right">vs Current</th>
                        </tr>
                      </thead>
                      <tbody>
                        {result.scenarios.map((s, i) => {
                          const isOptimal = s.price === result.optimal_price;
                          const isCurrent = s.price === result.current.price;
                          return (
                            <tr key={i} className={clsx(
                              "border-b last:border-0",
                              isOptimal ? "bg-brand-50" : isCurrent ? "bg-amber-50" : "hover:bg-gray-50"
                            )}>
                              <td className="px-4 py-2 font-medium">
                                MYR {s.price.toFixed(2)}
                                {isOptimal && <span className="ml-1.5 text-xs bg-brand-600 text-white px-1.5 py-0.5 rounded-full">Optimal</span>}
                                {isCurrent && <span className="ml-1.5 text-xs bg-amber-500 text-white px-1.5 py-0.5 rounded-full">Current</span>}
                              </td>
                              <td className="px-4 py-2 text-right text-gray-600">{s.units.toFixed(0)}</td>
                              <td className="px-4 py-2 text-right text-gray-600">MYR {s.revenue.toFixed(0)}</td>
                              <td className="px-4 py-2 text-right font-medium">{s.gross_profit < 0 ? <span className="text-red-600">MYR {s.gross_profit.toFixed(0)}</span> : `MYR ${s.gross_profit.toFixed(0)}`}</td>
                              <td className="px-4 py-2 text-right text-gray-600">{s.margin_pct.toFixed(1)}%</td>
                              <td className="px-4 py-2 text-right">
                                <span className={clsx("text-xs font-medium", s.vs_current_profit_pct > 0 ? "text-emerald-600" : s.vs_current_profit_pct < 0 ? "text-red-600" : "text-gray-400")}>
                                  {s.vs_current_profit_pct > 0 ? "+" : ""}{s.vs_current_profit_pct.toFixed(1)}%
                                </span>
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                </div>
              </>
            )}

            {!result && !mut.isPending && (
              <div className="card p-12 text-center text-gray-400">
                <Calculator className="w-12 h-12 mx-auto mb-3 opacity-30" />
                <p className="font-medium">Enter your pricing data</p>
                <p className="text-sm mt-1">Fill in the form and run the simulation to see optimal pricing scenarios</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
