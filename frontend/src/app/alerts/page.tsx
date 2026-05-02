"use client";
import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getAlerts, getAlertEvents, createAlert, toggleAlert, deleteAlert, getProducts } from "@/lib/api";
import { PageHeader } from "@/components/layout/PageHeader";
import { Plus, Bell, BellOff, Trash2, Zap } from "lucide-react";
import { formatDistanceToNow } from "date-fns";
import { clsx } from "clsx";
import type { Alert, Product } from "@/lib/types";

const ALERT_TYPES = [
  { value: "price_drop", label: "Price Drop" },
  { value: "price_spike", label: "Price Spike" },
  { value: "target_price", label: "Target Price" },
  { value: "back_in_stock", label: "Back in Stock" },
  { value: "competitor_change", label: "Competitor Change" },
];

function AddAlertModal({ onClose }: { onClose: () => void }) {
  const qc = useQueryClient();
  const { data: products = [] } = useQuery({ queryKey: ["products"], queryFn: getProducts });
  const mut = useMutation({
    mutationFn: createAlert,
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["alerts"] }); onClose(); },
  });
  const [form, setForm] = useState({
    product_id: "",
    alert_type: "price_drop",
    threshold_pct: "",
    threshold_price: "",
    direction: "below",
  });

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl w-full max-w-md shadow-xl">
        <div className="px-6 py-4 border-b flex items-center justify-between">
          <h2 className="font-semibold">Create Alert</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-xl">×</button>
        </div>
        <form onSubmit={e => {
          e.preventDefault();
          mut.mutate({
            ...form,
            threshold_pct: form.threshold_pct ? +form.threshold_pct : undefined,
            threshold_price: form.threshold_price ? +form.threshold_price : undefined,
          } as any);
        }} className="p-6 space-y-4">
          <div>
            <label className="text-sm font-medium text-gray-700">Product *</label>
            <select required value={form.product_id} onChange={e => setForm(p => ({ ...p, product_id: e.target.value }))}
              className="mt-1 w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500">
              <option value="">Select product…</option>
              {(products as Product[]).map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
            </select>
          </div>
          <div>
            <label className="text-sm font-medium text-gray-700">Alert Type *</label>
            <select value={form.alert_type} onChange={e => setForm(p => ({ ...p, alert_type: e.target.value }))}
              className="mt-1 w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500">
              {ALERT_TYPES.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
            </select>
          </div>
          {["price_drop", "price_spike"].includes(form.alert_type) && (
            <div>
              <label className="text-sm font-medium text-gray-700">Threshold (%)</label>
              <input type="number" step="0.1" value={form.threshold_pct} onChange={e => setForm(p => ({ ...p, threshold_pct: e.target.value }))}
                placeholder="e.g. 10 for 10% drop" className="mt-1 w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500" />
            </div>
          )}
          {form.alert_type === "target_price" && (
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-sm font-medium text-gray-700">Target Price (MYR)</label>
                <input type="number" step="0.01" value={form.threshold_price} onChange={e => setForm(p => ({ ...p, threshold_price: e.target.value }))}
                  placeholder="199.00" className="mt-1 w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500" />
              </div>
              <div>
                <label className="text-sm font-medium text-gray-700">Direction</label>
                <select value={form.direction} onChange={e => setForm(p => ({ ...p, direction: e.target.value }))}
                  className="mt-1 w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500">
                  <option value="below">Goes below</option>
                  <option value="above">Goes above</option>
                </select>
              </div>
            </div>
          )}
          <div className="flex gap-2 pt-2">
            <button type="button" onClick={onClose} className="btn-ghost flex-1">Cancel</button>
            <button type="submit" disabled={mut.isPending} className="btn-primary flex-1">
              {mut.isPending ? "Creating…" : "Create Alert"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default function AlertsPage() {
  const qc = useQueryClient();
  const { data: alerts = [] } = useQuery({ queryKey: ["alerts"], queryFn: getAlerts });
  const { data: events = [] } = useQuery({ queryKey: ["alert-events"], queryFn: () => getAlertEvents(20) });
  const { data: products = [] } = useQuery({ queryKey: ["products"], queryFn: getProducts });
  const toggleMut = useMutation({ mutationFn: toggleAlert, onSuccess: () => qc.invalidateQueries({ queryKey: ["alerts"] }) });
  const deleteMut = useMutation({ mutationFn: deleteAlert, onSuccess: () => qc.invalidateQueries({ queryKey: ["alerts"] }) });
  const [showModal, setShowModal] = useState(false);

  const productMap = Object.fromEntries((products as Product[]).map(p => [p.id, p.name]));

  return (
    <div>
      <PageHeader
        title="Smart Alerts"
        subtitle="Get notified when prices change"
        action={
          <button onClick={() => setShowModal(true)} className="btn-primary flex items-center gap-2">
            <Plus className="w-4 h-4" /> New Alert
          </button>
        }
      />

      <div className="px-6 space-y-6 pb-8">
        {/* Active Alerts */}
        <div className="card">
          <div className="px-5 py-4 border-b">
            <h2 className="font-semibold text-gray-800 flex items-center gap-2">
              <Bell className="w-4 h-4 text-brand-600" /> Active Alerts ({(alerts as Alert[]).filter(a => a.is_active).length})
            </h2>
          </div>
          {(alerts as Alert[]).length === 0 && (
            <p className="px-5 py-8 text-center text-sm text-gray-400">No alerts configured yet</p>
          )}
          <div className="divide-y">
            {(alerts as Alert[]).map(alert => (
              <div key={alert.id} className="px-5 py-3.5 flex items-center gap-3">
                <div className={clsx("w-8 h-8 rounded-full flex items-center justify-center", alert.is_active ? "bg-amber-100" : "bg-gray-100")}>
                  <Bell className={clsx("w-4 h-4", alert.is_active ? "text-amber-600" : "text-gray-400")} />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-sm text-gray-900 truncate">
                    {productMap[alert.product_id] ?? "Unknown Product"}
                  </p>
                  <p className="text-xs text-gray-400">
                    {ALERT_TYPES.find(t => t.value === alert.alert_type)?.label}
                    {alert.threshold_pct ? ` · ≥${alert.threshold_pct}%` : ""}
                    {alert.threshold_price ? ` · MYR ${alert.threshold_price}` : ""}
                    {alert.last_triggered ? ` · Last fired ${formatDistanceToNow(new Date(alert.last_triggered), { addSuffix: true })}` : ""}
                  </p>
                </div>
                <button onClick={() => toggleMut.mutate(alert.id)} className={clsx("text-xs px-2 py-1 rounded-md font-medium", alert.is_active ? "bg-green-50 text-green-700" : "bg-gray-100 text-gray-500")}>
                  {alert.is_active ? "Active" : "Paused"}
                </button>
                <button onClick={() => deleteMut.mutate(alert.id)} className="text-gray-300 hover:text-red-500">
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Alert Event History */}
        <div className="card">
          <div className="px-5 py-4 border-b">
            <h2 className="font-semibold text-gray-800 flex items-center gap-2">
              <Zap className="w-4 h-4 text-amber-500" /> Recent Events
            </h2>
          </div>
          {(events as any[]).length === 0 && (
            <p className="px-5 py-8 text-center text-sm text-gray-400">No alert events yet</p>
          )}
          <div className="divide-y">
            {(events as any[]).map((e: any) => (
              <div key={e.id} className="px-5 py-3 flex items-start gap-3">
                <div className="w-2 h-2 rounded-full bg-amber-400 mt-1.5 shrink-0" />
                <div>
                  <p className="text-sm text-gray-800">{e.message}</p>
                  <div className="flex gap-3 mt-0.5">
                    {e.old_price && <span className="text-xs text-gray-400">Was: MYR {e.old_price.toFixed(2)}</span>}
                    {e.new_price && <span className="text-xs text-gray-700 font-medium">Now: MYR {e.new_price.toFixed(2)}</span>}
                    <span className="text-xs text-gray-400">{formatDistanceToNow(new Date(e.fired_at), { addSuffix: true })}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {showModal && <AddAlertModal onClose={() => setShowModal(false)} />}
    </div>
  );
}
