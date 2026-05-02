export interface Product {
  id: string;
  name: string;
  brand: string | null;
  category: string | null;
  barcode: string | null;
  image_url: string | null;
  search_query: string | null;
  user_price: number | null;
  user_cost: number | null;
  created_at: string;
  updated_at: string;
}

export interface PlatformResult {
  platform: string;
  seller_name: string | null;
  price: number;
  original_price: number | null;
  discount_pct: number | null;
  currency: string;
  url: string | null;
  in_stock: boolean;
  rating: number | null;
  review_count: number | null;
  image_url: string | null;
  title: string;
}

export interface SearchResult {
  query: string;
  total_results: number;
  results: PlatformResult[];
  platforms_queried: string[];
  search_duration_ms: number;
}

export interface FairPriceAnalysis {
  product_id: string;
  product_name: string;
  min_price: number;
  max_price: number;
  mean_price: number;
  median_price: number;
  std_dev: number;
  fair_price_low: number;
  fair_price_high: number;
  cheap_threshold: number;
  expensive_threshold: number;
  total_listings: number;
  platforms_covered: string[];
  last_updated: string;
}

export interface MarketPosition {
  user_price: number;
  market_median: number;
  percentile: number;
  classification: "Cheap" | "Fair" | "Expensive";
  vs_median_pct: number;
  recommendation: string;
  platform_breakdown: Array<{ platform: string; min: number; max: number; avg: number }>;
}

export interface Alert {
  id: string;
  product_id: string;
  alert_type: string;
  threshold_pct: number | null;
  threshold_price: number | null;
  direction: string | null;
  platform_filter: string | null;
  is_active: boolean;
  last_triggered: string | null;
  created_at: string;
}

export interface AlertEvent {
  id: string;
  alert_id: string;
  message: string;
  old_price: number | null;
  new_price: number | null;
  platform: string | null;
  fired_at: string;
}

export interface ROIInput {
  selling_price: number;
  cost_price: number;
  monthly_units: number;
  price_elasticity?: number;
  market_median_price?: number;
}

export interface PriceScenario {
  price: number;
  units: number;
  revenue: number;
  gross_profit: number;
  margin_pct: number;
  vs_current_revenue_pct: number;
  vs_current_profit_pct: number;
}

export interface ROIOutput {
  current: PriceScenario;
  break_even_price: number;
  break_even_units: number;
  optimal_price: number;
  optimal_revenue: number;
  optimal_margin_pct: number;
  scenarios: PriceScenario[];
  recommendation: string;
  market_position: string | null;
}

export interface DashboardStats {
  total_products_tracked: number;
  price_checks_last_24h: number;
  platforms_active: number;
  avg_tracked_price_myr: number;
}

export const PLATFORM_LABELS: Record<string, string> = {
  lazada: "Lazada",
  shopee: "Shopee",
  aeon: "AEON",
  jaya_grocer: "Jaya Grocer",
  "99speedmart": "99 Speedmart",
  giant: "Giant",
  lotus: "Lotus's",
};

export const PLATFORM_COLORS: Record<string, string> = {
  lazada: "#f97316",
  shopee: "#ef4444",
  aeon: "#3b82f6",
  jaya_grocer: "#10b981",
  "99speedmart": "#8b5cf6",
  giant: "#06b6d4",
  lotus: "#ec4899",
};
