import { NavLink, Outlet, useLocation } from "react-router-dom";

import { useAuth } from "../lib/auth";
import { Icon } from "./Icons";

type NavItem = {
  to: string;
  label: string;
  icon: "overview" | "today" | "performance" | "stability" | "learning" | "providers" | "operations" | "guide";
  end?: boolean;
};

const NAV_ITEMS: NavItem[] = [
  { to: "/", label: "Overview", icon: "overview", end: true },
  { to: "/today", label: "Today", icon: "today" },
  { to: "/performance", label: "Performance", icon: "performance" },
  { to: "/stability", label: "Stability", icon: "stability" },
  { to: "/learning", label: "Learning", icon: "learning" },
  { to: "/providers", label: "Providers", icon: "providers" },
  { to: "/guide", label: "Guide", icon: "guide" },
  { to: "/operations", label: "Operations", icon: "operations" },
];

export function AppShell() {
  const { logout } = useAuth();
  const location = useLocation();

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="topbar__brand">
          <div className="brand-mark" />
          <div>
            <p className="eyebrow">Operator Dashboard</p>
            <h1>NBA Oracle</h1>
          </div>
        </div>
        <nav className="topnav" aria-label="Primary">
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) => (isActive ? "topnav__link topnav__link--active" : "topnav__link")}
            >
              <Icon name={item.icon} className="nav-icon" />
              {item.label}
            </NavLink>
          ))}
        </nav>
        <div className="topbar__actions">
          <div className="session-chip">
            <span className="session-chip__dot" />
            <span>{NAV_ITEMS.find((item) => item.to === location.pathname)?.label ?? "Overview"}</span>
          </div>
          <button type="button" className="button button--ghost" onClick={logout}>
            Sign out
          </button>
        </div>
      </header>
      <main className="page-shell">
        <Outlet />
      </main>
    </div>
  );
}
