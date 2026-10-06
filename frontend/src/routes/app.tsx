import { createFileRoute, redirect } from "@tanstack/react-router";
import { AppShell } from "@/components/layout/AppShell";
import { getToken, getRole, getPermissions } from "@/lib/api/auth";

export const Route = createFileRoute("/app")({
  beforeLoad: ({ location }) => {
    if (location.pathname === "/app/login") return;
    if (!getToken()) {
      throw redirect({ to: "/app/login" });
    }
    const role = getRole();
    if (role === "admin") {
      throw redirect({ to: "/app/login" });
    }
    const permissions = getPermissions();
    if (!permissions.length) {
      throw redirect({ to: "/app/login" });
    }
    if (location.pathname === "/app" || location.pathname === "/app/") {
      throw redirect({ to: "/app/dashboard" });
    }
  },
  component: () => <AppShell portal="university" />,
});
