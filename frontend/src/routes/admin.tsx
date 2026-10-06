import { createFileRoute, redirect } from "@tanstack/react-router";
import { AppShell } from "@/components/layout/AppShell";
import { getToken, getRole } from "@/lib/api/auth";

export const Route = createFileRoute("/admin")({
  beforeLoad: ({ location }) => {
    if (location.pathname === "/admin/login") return;
    if (!getToken()) {
      throw redirect({ to: "/admin/login" });
    }
    const role = getRole();
    if (role !== "admin") {
      throw redirect({ to: "/admin/login" });
    }
    if (location.pathname === "/admin" || location.pathname === "/admin/") {
      throw redirect({ to: "/admin/dashboard" });
    }
  },
  component: () => <AppShell portal="admin" />,
});
