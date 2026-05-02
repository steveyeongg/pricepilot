import axios from "axios";
import type {
  Product, SearchResult, FairPriceAnalysis, MarketPosition,
  Alert, AlertEvent, ROIInput, ROIOutput, DashboardStats,
} from "./types";

const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const http = axios.create({ baseURL: BASE, timeout: 30_000 });

// Products
export const getProducts = () => http.get<Product[]>("/api/products").then(r => r.data);
export const createProduct = (body: Partial<Product>) => http.post<Product>("/api/products", body).then(r => r.data);
export const updateProduct = (id: string, body: Partial<Product>) => http.patch<Product>(`/api/products/${id}`, body).then(r => r.data);
export const deleteProduct = (id: string) => http.delete(`/api/products/${id}`);

// Search
export const searchPrices = (q: string, platforms?: string, limit = 10) =>
  http.get<SearchResult>("/api/search", { params: { q, platforms, limit } }).then(r => r.data);

export const getFairPriceLive = (q: string, platforms?: string) =>
  http.get<FairPriceAnalysis>("/api/search/fair-price", { params: { q, platforms } }).then(r => r.data);

// Analytics
export const getProductFairPrice = (id: string) =>
  http.get<FairPriceAnalysis>(`/api/analytics/products/${id}/fair-price`).then(r => r.data);

export const getProductPosition = (id: string) =>
  http.get<MarketPosition>(`/api/analytics/products/${id}/position`).then(r => r.data);

export const getProductHistory = (id: string, days = 30, platform?: string) =>
  http.get(`/api/analytics/products/${id}/history`, { params: { days, platform } }).then(r => r.data);

export const getDashboardStats = () =>
  http.get<DashboardStats>("/api/analytics/dashboard").then(r => r.data);

// Alerts
export const getAlerts = () => http.get<Alert[]>("/api/alerts").then(r => r.data);
export const createAlert = (body: Partial<Alert>) => http.post<Alert>("/api/alerts", body).then(r => r.data);
export const toggleAlert = (id: string) => http.patch<Alert>(`/api/alerts/${id}/toggle`).then(r => r.data);
export const deleteAlert = (id: string) => http.delete(`/api/alerts/${id}`);
export const getAlertEvents = (limit = 50) =>
  http.get<AlertEvent[]>("/api/alerts/events/recent", { params: { limit } }).then(r => r.data);

// ROI
export const simulateROI = (body: ROIInput) =>
  http.post<ROIOutput>("/api/roi/simulate", body).then(r => r.data);
