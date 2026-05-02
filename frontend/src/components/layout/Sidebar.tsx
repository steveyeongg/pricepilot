"use client";
import { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard, Search, Package, BarChart3,
  Bell, Calculator, Plane, ChevronRight, Menu, X,
} from "lucide-react";
import { clsx } from "clsx";

const NAV = [
  { href: "/",          icon: LayoutDashboard, label: "Dashboard" },
  { href: "/search",    icon: Search,          label: "Search & Compare" },
  { href: "/products",  icon: Package,         label: "Tracked Products" },
  { href: "/analytics", icon: BarChart3,       label: "Analytics" },
  { href: "/alerts",    icon: Bell,            label: "Smart Alerts" },
  { href: "/roi",       icon: Calculator,      label: "ROI Calculator" },
];

function Logo() {
  return (
    <div className="flex items-center gap-2.5">
      <div className="w-8 h-8 bg-brand-600 rounded-lg flex items-center justify-center shrink-0">
        <Plane className="w-4 h-4 text-white" />
      </div>
      <div>
        <p className="font-bold text-gray-900 text-sm leading-none">PricePilot</p>
        <p className="text-xs text-gray-400 mt-0.5">Smart Pricing Co-Pilot</p>
      </div>
    </div>
  );
}

function NavLinks({ onSelect }: { onSelect?: () => void }) {
  const path = usePathname();
  return (
    <nav className="flex-1 px-3 py-4 space-y-0.5 overflow-y-auto">
      {NAV.map(({ href, icon: Icon, label }) => {
        const active = path === href || (href !== "/" && path.startsWith(href));
        return (
          <Link
            key={href}
            href={href}
            onClick={onSelect}
            className={clsx(
              "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors group",
              active
                ? "bg-brand-50 text-brand-700"
                : "text-gray-600 hover:bg-gray-50 hover:text-gray-900"
            )}
          >
            <Icon
              className={clsx(
                "w-4 h-4 shrink-0",
                active ? "text-brand-600" : "text-gray-400 group-hover:text-gray-600"
              )}
            />
            <span className="flex-1">{label}</span>
            {active && <ChevronRight className="w-3.5 h-3.5 text-brand-400" />}
          </Link>
        );
      })}
    </nav>
  );
}

function SidebarFooter() {
  return (
    <div className="px-5 py-4 border-t">
      <p className="text-xs text-gray-400 leading-relaxed">
        Know the right price — instantly, automatically and with confidence.
      </p>
    </div>
  );
}

export function Sidebar() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const pathname = usePathname();

  // Close drawer whenever the route changes (handles back-button navigation too)
  useEffect(() => {
    setMobileOpen(false);
  }, [pathname]);

  // Prevent body scroll while drawer is open
  useEffect(() => {
    if (mobileOpen) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }
    return () => { document.body.style.overflow = ""; };
  }, [mobileOpen]);

  return (
    <>
      {/* ─── MOBILE TOP BAR ─────────────────────────────────────────────── */}
      <div className="md:hidden fixed top-0 inset-x-0 z-30 h-14 bg-white border-b flex items-center px-4 gap-3 shadow-sm">
        <button
          onClick={() => setMobileOpen(true)}
          className="p-2 rounded-lg hover:bg-gray-100 transition-colors -ml-1"
          aria-label="Open navigation menu"
        >
          <Menu className="w-5 h-5 text-gray-600" />
        </button>
        <Logo />
      </div>

      {/* ─── MOBILE DRAWER ──────────────────────────────────────────────── */}
      {/* Backdrop */}
      <div
        className={clsx(
          "md:hidden fixed inset-0 z-40 bg-black/50 transition-opacity duration-300",
          mobileOpen ? "opacity-100 pointer-events-auto" : "opacity-0 pointer-events-none"
        )}
        onClick={() => setMobileOpen(false)}
        aria-hidden="true"
      />

      {/* Drawer panel */}
      <aside
        className={clsx(
          "md:hidden fixed top-0 left-0 z-50 h-full w-72 max-w-[85vw] bg-white shadow-2xl",
          "flex flex-col transform transition-transform duration-300 ease-in-out",
          mobileOpen ? "translate-x-0" : "-translate-x-full"
        )}
      >
        {/* Drawer header */}
        <div className="h-14 px-4 border-b flex items-center justify-between shrink-0">
          <Logo />
          <button
            onClick={() => setMobileOpen(false)}
            className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
            aria-label="Close navigation menu"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* Nav links — close drawer on selection */}
        <NavLinks onSelect={() => setMobileOpen(false)} />
        <SidebarFooter />
      </aside>

      {/* ─── DESKTOP SIDEBAR (unchanged) ────────────────────────────────── */}
      <aside className="hidden md:flex w-60 bg-white border-r flex-col shrink-0">
        <div className="px-5 py-5 border-b">
          <Logo />
        </div>
        <NavLinks />
        <SidebarFooter />
      </aside>
    </>
  );
}
