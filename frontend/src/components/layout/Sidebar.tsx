"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard, Search, Package, BarChart3,
  Bell, Calculator, Plane, ChevronRight,
} from "lucide-react";
import { clsx } from "clsx";

const NAV = [
  { href: "/", icon: LayoutDashboard, label: "Dashboard" },
  { href: "/search", icon: Search, label: "Search & Compare" },
  { href: "/products", icon: Package, label: "Tracked Products" },
  { href: "/analytics", icon: BarChart3, label: "Analytics" },
  { href: "/alerts", icon: Bell, label: "Smart Alerts" },
  { href: "/roi", icon: Calculator, label: "ROI Calculator" },
];

export function Sidebar() {
  const path = usePathname();

  return (
    <aside className="w-60 bg-white border-r flex flex-col shrink-0">
      {/* Logo */}
      <div className="px-5 py-5 border-b">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 bg-brand-600 rounded-lg flex items-center justify-center">
            <Plane className="w-4 h-4 text-white" />
          </div>
          <div>
            <p className="font-bold text-gray-900 text-sm leading-none">PricePilot</p>
            <p className="text-xs text-gray-400 mt-0.5">Smart Pricing Co-Pilot</p>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 space-y-0.5">
        {NAV.map(({ href, icon: Icon, label }) => {
          const active = path === href || (href !== "/" && path.startsWith(href));
          return (
            <Link
              key={href}
              href={href}
              className={clsx(
                "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors group",
                active
                  ? "bg-brand-50 text-brand-700"
                  : "text-gray-600 hover:bg-gray-50 hover:text-gray-900"
              )}
            >
              <Icon className={clsx("w-4 h-4 shrink-0", active ? "text-brand-600" : "text-gray-400 group-hover:text-gray-600")} />
              <span className="flex-1">{label}</span>
              {active && <ChevronRight className="w-3.5 h-3.5 text-brand-400" />}
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="px-5 py-4 border-t">
        <p className="text-xs text-gray-400 leading-relaxed">
          Know the right price — instantly, automatically and with confidence.
        </p>
      </div>
    </aside>
  );
}
