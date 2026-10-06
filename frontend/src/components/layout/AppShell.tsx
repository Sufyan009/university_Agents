import { Link, useLocation, Outlet, useNavigate } from "@tanstack/react-router";
import {
  LayoutDashboard,
  GraduationCap,
  BookOpen,
  Layers,
  ClipboardList,
  Award,
  HelpCircle,
  Mic,
  Users,
  Settings,
  Building2,
  Compass,
  ChevronDown,
  Search,
  Bell,
  Menu,
  X,
  LogOut,
  PhoneCall,
} from "lucide-react";
import { useState, useEffect } from "react";
import { cn } from "@/lib/utils";
import { getUserProfile, getRole, logout } from "@/lib/api/auth";
import { getUniversityProfile } from "@/lib/api/university";

interface NavItem {
  to: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
}

const universityNav: NavItem[] = [
  { to: "/app/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { to: "/app/courses", label: "Courses", icon: BookOpen },
  { to: "/app/subjects", label: "Subjects", icon: Layers },
  { to: "/app/admissions", label: "Admissions", icon: ClipboardList },
  { to: "/app/scholarships", label: "Scholarships", icon: Award },
  { to: "/app/faqs", label: "FAQs", icon: HelpCircle },
  { to: "/app/voice-agent", label: "Voice Agent", icon: Mic },
  { to: "/app/users", label: "Users & Roles", icon: Users },
  { to: "/app/settings", label: "Settings", icon: Settings },
];

const adminNav: NavItem[] = [
  { to: "/admin/dashboard", label: "Overview", icon: LayoutDashboard },
  { to: "/admin/universities", label: "Universities", icon: Building2 },
  { to: "/admin/onboarding", label: "Onboarding", icon: Compass },
];

interface AppShellProps {
  portal: "university" | "admin";
}

export function AppShell({ portal }: AppShellProps) {
  const location = useLocation();
  const loginPath = portal === "university" ? "/app/login" : "/admin/login";
  if (location.pathname === loginPath) return <Outlet />;
  return <AppShellInner portal={portal} />;
}

function AppShellInner({ portal }: AppShellProps) {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [universityName, setUniversityName] = useState("Loading...");
  const nav = portal === "university" ? universityNav : adminNav;
  const portalLabel = portal === "university" ? universityName : "Scholaria Admin";
  const portalSub = portal === "university" ? "University Portal" : "Platform Console";

  useEffect(() => {
    if (portal === "university") {
      getUniversityProfile()
        .then((p) => setUniversityName(p.name || "University"))
        .catch(() => setUniversityName("University"));
    }
  }, [portal]);

  return (
    <div className="flex min-h-screen w-full bg-background">
      <aside className="hidden lg:flex w-64 shrink-0 flex-col border-r border-border-subtle bg-sidebar">
        <SidebarContent nav={nav} portalLabel={portalLabel} portalSub={portalSub} portal={portal} />
      </aside>

      {mobileOpen && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <div className="absolute inset-0 bg-foreground/40 backdrop-blur-sm" onClick={() => setMobileOpen(false)} />
          <aside className="absolute left-0 top-0 h-full w-72 bg-sidebar border-r border-border-subtle flex flex-col animate-in slide-in-from-left">
            <button className="absolute right-3 top-3 p-2 rounded-md hover:bg-muted" onClick={() => setMobileOpen(false)} aria-label="Close menu">
              <X className="h-4 w-4" />
            </button>
            <SidebarContent nav={nav} portalLabel={portalLabel} portalSub={portalSub} portal={portal} onNavigate={() => setMobileOpen(false)} />
          </aside>
        </div>
      )}

      <div className="flex-1 flex flex-col min-w-0">
        <Topbar onMenuClick={() => setMobileOpen(true)} portal={portal} />
        <main className="flex-1 overflow-x-hidden">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

function SidebarContent({
  nav,
  portalLabel,
  portalSub,
  portal,
  onNavigate,
}: {
  nav: NavItem[];
  portalLabel: string;
  portalSub: string;
  portal: "university" | "admin";
  onNavigate?: () => void;
}) {
  const location = useLocation();
  const swapPortal = portal === "university" ? "/admin/dashboard" : "/app/dashboard";
  const swapLabel = portal === "university" ? "Switch to Admin" : "Switch to University";

  return (
    <>
      <div className="px-5 pt-5 pb-4">
        <Link to="/" className="flex items-center gap-2.5">
          <div className="h-8 w-8 rounded-lg bg-gradient-primary flex items-center justify-center shadow-glow">
            <GraduationCap className="h-4 w-4 text-primary-foreground" />
          </div>
          <span className="font-bold text-base tracking-tight">Scholaria</span>
        </Link>

        <button className="mt-5 w-full flex items-center justify-between px-3 py-2.5 rounded-lg border border-border-subtle bg-surface hover:bg-muted transition-smooth text-left">
          <div className="min-w-0">
            <div className="text-sm font-semibold truncate">{portalLabel}</div>
            <div className="text-xs text-muted-foreground truncate">{portalSub}</div>
          </div>
          <ChevronDown className="h-4 w-4 text-muted-foreground shrink-0" />
        </button>
      </div>

      <nav className="flex-1 px-3 space-y-0.5 overflow-y-auto">
        {nav.map((item) => {
          const isActive = location.pathname === item.to || location.pathname.startsWith(item.to + "/");
          const Icon = item.icon;
          return (
            <Link
              key={item.to}
              to={item.to}
              onClick={onNavigate}
              className={cn(
                "flex items-center gap-2.5 px-3 py-2 rounded-md text-sm font-medium transition-smooth",
                isActive
                  ? "bg-sidebar-accent text-sidebar-accent-foreground"
                  : "text-sidebar-foreground hover:bg-muted hover:text-foreground",
              )}
            >
              <Icon className="h-4 w-4" />
              {item.label}
            </Link>
          );
        })}
      </nav>

      <div className="p-3 border-t border-border-subtle">
        <Link
          to={swapPortal}
          onClick={onNavigate}
          className="flex items-center gap-2.5 px-3 py-2 rounded-md text-sm font-medium text-muted-foreground hover:bg-muted hover:text-foreground transition-smooth"
        >
          <Compass className="h-4 w-4" />
          {swapLabel}
        </Link>
      </div>
    </>
  );
}

function Topbar({ onMenuClick, portal }: { onMenuClick: () => void; portal: "university" | "admin" }) {
  const [user, setUser] = useState<{ name: string; role: string } | null>(null);
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const loadUser = async () => {
      const roleValue = getRole();
      const roleDisplay = roleValue ? roleValue.charAt(0).toUpperCase() + roleValue.slice(1) : "User";
      try {
        const profile = await getUserProfile();
        setUser({ name: profile.name || profile.email, role: roleDisplay });
      } catch {
        setUser({ name: "User", role: roleDisplay });
      }
    };
    loadUser();
  }, []);

  useEffect(() => {
    if (!dropdownOpen) return;
    const handleClickOutside = (e: MouseEvent) => {
      const target = e.target as HTMLElement;
      if (!target.closest("[data-user-menu]")) setDropdownOpen(false);
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [dropdownOpen]);

  const initials =
    user?.name
      ?.split(" ")
      .map((n) => n[0])
      .join("")
      .toUpperCase() || "?";

  const handleLogout = () => {
    logout();
    navigate({ to: portal === "admin" ? "/admin/login" : "/app/login" });
  };

  return (
    <header className="h-16 border-b border-border-subtle bg-surface/80 backdrop-blur-md sticky top-0 z-40">
      <div className="h-full px-4 lg:px-8 flex items-center gap-3">
        <button className="lg:hidden p-2 -ml-2 rounded-md hover:bg-muted" onClick={onMenuClick} aria-label="Open menu">
          <Menu className="h-5 w-5" />
        </button>

        <div className="hidden md:flex flex-1 max-w-md">
          <div className="relative w-full">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <input
              type="text"
              placeholder={portal === "university" ? "Search courses, subjects…" : "Search universities…"}
              className="w-full h-9 pl-9 pr-3 rounded-md border border-border bg-background text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent transition-smooth"
            />
          </div>
        </div>

        <div className="flex-1 md:hidden" />

        <div className="flex items-center gap-1">
          <button className="relative p-2 rounded-md hover:bg-muted text-muted-foreground hover:text-foreground transition-smooth" aria-label="Notifications">
            <Bell className="h-4 w-4" />
            <span className="absolute top-1.5 right-1.5 h-1.5 w-1.5 bg-destructive rounded-full" />
          </button>
          <div className="relative ml-2 pl-3 border-l border-border-subtle" data-user-menu>
            <button
              className="flex items-center gap-2.5 rounded-md px-1 py-1 hover:bg-muted transition-smooth"
              onClick={() => setDropdownOpen((v) => !v)}
              aria-label="User menu"
            >
              <div className="hidden sm:block text-right">
                <div className="text-sm font-semibold leading-tight">{user?.name || "Loading…"}</div>
                <div className="text-xs text-muted-foreground leading-tight">{user?.role || ""}</div>
              </div>
              <div className="h-8 w-8 rounded-full bg-gradient-primary flex items-center justify-center text-primary-foreground text-xs font-bold shadow-card">
                {initials}
              </div>
            </button>

            {dropdownOpen && (
              <div className="absolute right-0 top-full mt-2 w-48 rounded-md border border-border bg-background shadow-lg z-50 py-1">
                <div className="px-3 py-2 border-b border-border">
                  <div className="text-sm font-semibold truncate">{user?.name}</div>
                  <div className="text-xs text-muted-foreground">{user?.role}</div>
                </div>
                <button className="w-full flex items-center gap-2 px-3 py-2 text-sm text-destructive hover:bg-muted transition-smooth" onClick={handleLogout}>
                  <LogOut className="h-4 w-4" />
                  Sign out
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
