"use client";
import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getProducts, createProduct, deleteProduct } from "@/lib/api";
import { PageHeader } from "@/components/layout/PageHeader";
import { Plus, Trash2, Package, ExternalLink } from "lucide-react";
import { formatDistanceToNow } from "date-fns";
import type { Product } from "@/lib/types";

function AddProductModal({ onClose }: { onClose: () => void }) {
  const qc = useQueryClient();
  const mut = useMutation({
    mutationFn: createProduct,
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["products"] }); onClose(); },
  });
  const [form, setForm] = useState({ name: "", brand: "", category: "", search_query: "", user_price: "", user_cost: "" });

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl w-full max-w-md shadow-xl">
        <div className="px-6 py-4 border-b flex items-center justify-between">
          <h2 className="font-semibold">Add Product to Track</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-xl leading-none">×</button>
        </div>
        <form
          onSubmit={e => { e.preventDefault(); mut.mutate({ ...form, user_price: form.user_price ? +form.user_price : undefined, user_cost: form.user_cost ? +form.user_cost : undefined }); }}
          className="p-6 space-y-4"
        >
          <div>
            <label className="text-sm font-medium text-gray-700">Product Name *</label>
            <input required value={form.name} onChange={e => setForm(p => ({ ...p, name: e.target.value }))}
              placeholder="e.g. iPhone 15 Pro 256GB" className="mt-1 w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500" />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-sm font-medium text-gray-700">Brand</label>
              <input value={form.brand} onChange={e => setForm(p => ({ ...p, brand: e.target.value }))}
                placeholder="Apple" className="mt-1 w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500" />
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700">Category</label>
              <input value={form.category} onChange={e => setForm(p => ({ ...p, category: e.target.value }))}
                placeholder="Electronics" className="mt-1 w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500" />
            </div>
          </div>
          <div>
            <label className="text-sm font-medium text-gray-700">Search Query (overrides name for scraping)</label>
            <input value={form.search_query} onChange={e => setForm(p => ({ ...p, search_query: e.target.value }))}
              placeholder="e.g. iphone 15 pro 256" className="mt-1 w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500" />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-sm font-medium text-gray-700">Your Selling Price (MYR)</label>
              <input type="number" step="0.01" value={form.user_price} onChange={e => setForm(p => ({ ...p, user_price: e.target.value }))}
                placeholder="299.00" className="mt-1 w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500" />
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700">Your Cost Price (MYR)</label>
              <input type="number" step="0.01" value={form.user_cost} onChange={e => setForm(p => ({ ...p, user_cost: e.target.value }))}
                placeholder="150.00" className="mt-1 w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500" />
            </div>
          </div>
          <div className="flex gap-2 pt-2">
            <button type="button" onClick={onClose} className="btn-ghost flex-1">Cancel</button>
            <button type="submit" disabled={mut.isPending} className="btn-primary flex-1">
              {mut.isPending ? "Adding…" : "Add Product"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default function ProductsPage() {
  const qc = useQueryClient();
  const { data: products = [], isLoading } = useQuery({ queryKey: ["products"], queryFn: getProducts });
  const deleteMut = useMutation({ mutationFn: deleteProduct, onSuccess: () => qc.invalidateQueries({ queryKey: ["products"] }) });
  const [showModal, setShowModal] = useState(false);

  return (
    <div>
      <PageHeader
        title="Tracked Products"
        subtitle="Products being monitored for price changes"
        action={
          <button onClick={() => setShowModal(true)} className="btn-primary flex items-center gap-2">
            <Plus className="w-4 h-4" /> Add Product
          </button>
        }
      />

      <div className="px-6 pb-8">
        {isLoading && <p className="text-sm text-gray-400 py-8 text-center">Loading…</p>}

        {!isLoading && products.length === 0 && (
          <div className="text-center py-16 text-gray-400">
            <Package className="w-12 h-12 mx-auto mb-3 opacity-30" />
            <p className="font-medium">No products tracked yet</p>
            <p className="text-sm mt-1">Add a product to start monitoring prices</p>
            <button onClick={() => setShowModal(true)} className="btn-primary mt-4">
              <Plus className="w-4 h-4 inline mr-1.5" /> Add First Product
            </button>
          </div>
        )}

        <div className="grid gap-3">
          {products.map((p: Product) => (
            <div key={p.id} className="card px-5 py-4 flex items-center gap-4">
              <div className="w-10 h-10 bg-brand-50 rounded-lg flex items-center justify-center shrink-0">
                <Package className="w-5 h-5 text-brand-600" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="font-medium text-gray-900 truncate">{p.name}</p>
                <p className="text-xs text-gray-400 mt-0.5">
                  {[p.brand, p.category].filter(Boolean).join(" · ")}
                  {" · "}Added {formatDistanceToNow(new Date(p.created_at), { addSuffix: true })}
                </p>
              </div>
              {p.user_price && (
                <div className="text-right shrink-0">
                  <p className="text-xs text-gray-400">Your price</p>
                  <p className="font-semibold text-gray-900">MYR {Number(p.user_price).toFixed(2)}</p>
                  {p.user_cost && (
                    <p className="text-xs text-gray-400">Cost: MYR {Number(p.user_cost).toFixed(2)}</p>
                  )}
                </div>
              )}
              <button
                onClick={() => deleteMut.mutate(p.id)}
                className="text-gray-300 hover:text-red-500 transition-colors"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          ))}
        </div>
      </div>

      {showModal && <AddProductModal onClose={() => setShowModal(false)} />}
    </div>
  );
}
