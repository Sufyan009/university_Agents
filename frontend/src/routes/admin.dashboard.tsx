import { createFileRoute, Link } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { Building2, Compass, Plus } from "lucide-react";

import { PageHeader } from "@/components/shared/PageHeader";
import { StatCard } from "@/components/shared/StatCard";
import { adminListUniversities } from "@/lib/api/admin-universities";

export const Route = createFileRoute("/admin/dashboard")({
  head: () => ({
    meta: [{ title: "Overview — Scholaria Admin" }],
  }),
  component: AdminDashboard,
});

function AdminDashboard() {
  const { data, isLoading, error } = useQuery({
    queryKey: ["admin", "universities", "overview"],
    queryFn: () => adminListUniversities({ page: 1, page_size: 8 }),
  });

  const total = data?.total ?? 0;
  const recent = data?.items ?? [];

  return (
    <div className="mx-auto max-w-[1200px] px-4 py-6 lg:px-8 lg:py-8">
      <PageHeader
        title="Platform Overview"
        description="Universities onboarded to the voice agent platform."
        actions={
          <Link
            to="/admin/onboarding"
            className="inline-flex items-center gap-2 rounded-lg bg-gradient-primary px-4 py-2 text-sm font-semibold text-primary-foreground shadow-glow transition-smooth hover:shadow-elevated"
          >
            <Plus className="h-4 w-4" />
            Onboard university
          </Link>
        }
      />

      {error && (
        <div className="mb-4 rounded-lg border border-destructive bg-destructive/10 p-3 text-sm text-destructive">
          {error instanceof Error ? error.message : "Failed to load"}
        </div>
      )}

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <StatCard label="Universities" value={isLoading ? "…" : String(total)} icon={Building2} accent="primary" />
        <Link to="/admin/universities" className="block">
          <StatCard label="Manage" value="Universities" icon={Building2} accent="info" />
        </Link>
        <Link to="/admin/onboarding" className="block">
          <StatCard label="Onboard" value="New university" icon={Compass} accent="success" />
        </Link>
      </div>

      <div className="mt-6 rounded-xl border border-border-subtle bg-surface shadow-card">
        <div className="flex items-center justify-between border-b border-border-subtle px-5 py-4">
          <div>
            <h3 className="font-semibold">Recent universities</h3>
            <p className="mt-0.5 text-xs text-muted-foreground">Most recently added.</p>
          </div>
          <Link to="/admin/universities" className="text-sm text-primary hover:underline">
            View all →
          </Link>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="border-b border-border-subtle">
              <tr className="text-left text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                <th className="px-4 py-3">Name</th>
                <th className="px-4 py-3">Phone</th>
                <th className="px-4 py-3">Location</th>
                <th className="px-4 py-3">Created</th>
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                <tr>
                  <td colSpan={4} className="px-4 py-12 text-center text-muted-foreground">Loading…</td>
                </tr>
              ) : recent.length === 0 ? (
                <tr>
                  <td colSpan={4} className="px-4 py-12 text-center text-muted-foreground">
                    No universities yet. Onboard your first one.
                  </td>
                </tr>
              ) : (
                recent.map((u) => (
                  <tr key={u.id} className="border-b border-border-subtle last:border-0 hover:bg-muted/40 transition-smooth">
                    <td className="px-4 py-3 font-medium">{u.name}</td>
                    <td className="px-4 py-3 text-muted-foreground">{u.phone || "—"}</td>
                    <td className="px-4 py-3 text-muted-foreground">
                      {[u.location?.city, u.location?.country].filter(Boolean).join(", ") || "—"}
                    </td>
                    <td className="px-4 py-3 text-xs text-muted-foreground">
                      {new Date(u.created_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
