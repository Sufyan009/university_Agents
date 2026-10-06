import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { BookOpen, ClipboardCheck, Phone } from "lucide-react";

import { PageHeader } from "@/components/shared/PageHeader";
import { StatCard } from "@/components/shared/StatCard";
import { StatusPill } from "@/components/shared/StatusPill";
import { listCourses } from "@/lib/api/courses";
import { getAdmissionInfo } from "@/lib/api/admissions";
import { listCalls, type CallSession } from "@/lib/api/calls";

export const Route = createFileRoute("/app/dashboard")({
  head: () => ({
    meta: [
      { title: "Dashboard — Scholaria" },
      {
        name: "description",
        content: "Overview of courses, admissions, and recent voice agent calls.",
      },
    ],
  }),
  component: DashboardPage,
});

const callTone: Record<string, "success" | "warning" | "info" | "danger" | "neutral"> = {
  active: "info",
  in_progress: "info",
  completed: "success",
  ended: "success",
  failed: "danger",
  error: "danger",
};

function DashboardPage() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [totalCourses, setTotalCourses] = useState(0);
  const [admissionsConfigured, setAdmissionsConfigured] = useState(false);
  const [calls, setCalls] = useState<CallSession[]>([]);

  useEffect(() => {
    const load = async () => {
      try {
        setLoading(true);
        setError(null);

        const [coursesRes, admissionRes, callsRes] = await Promise.allSettled([
          listCourses({ page_size: 1 }),
          getAdmissionInfo(),
          listCalls(),
        ]);

        if (coursesRes.status === "fulfilled") {
          setTotalCourses(coursesRes.value.total);
        } else {
          throw coursesRes.reason;
        }

        // admissions: ok -> configured, 404 -> not configured
        if (admissionRes.status === "fulfilled") {
          setAdmissionsConfigured(true);
        } else {
          setAdmissionsConfigured(false);
        }

        if (callsRes.status === "fulfilled") {
          setCalls(callsRes.value);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load dashboard");
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  if (loading) {
    return (
      <div className="mx-auto max-w-[1200px] px-4 py-6 lg:px-8 lg:py-8">
        <div className="text-center text-muted-foreground">Loading dashboard...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="mx-auto max-w-[1200px] px-4 py-6 lg:px-8 lg:py-8">
        <div className="rounded-lg border border-destructive bg-destructive/10 p-3 text-sm text-destructive">
          {error}
        </div>
      </div>
    );
  }

  const recentCalls = [...calls]
    .sort((a, b) => new Date(b.started_at).getTime() - new Date(a.started_at).getTime())
    .slice(0, 8);

  return (
    <div className="mx-auto max-w-[1200px] px-4 py-6 lg:px-8 lg:py-8">
      <PageHeader
        title="Dashboard"
        description="A quick overview of your university's configuration and recent activity."
      />

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <StatCard label="Total Courses" value={String(totalCourses)} icon={BookOpen} accent="primary" />
        <StatCard
          label="Admissions"
          value={admissionsConfigured ? "Configured" : "Not set"}
          icon={ClipboardCheck}
          accent={admissionsConfigured ? "success" : "neutral"}
        />
        <StatCard label="Recent Calls" value={String(calls.length)} icon={Phone} accent="info" />
      </div>

      <div className="mt-6 rounded-xl border border-border-subtle bg-surface shadow-card">
        <div className="border-b border-border-subtle px-5 py-4">
          <h3 className="font-semibold">Recent calls</h3>
          <p className="mt-0.5 text-xs text-muted-foreground">Latest voice agent sessions.</p>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="border-b border-border-subtle bg-surface-elevated">
              <tr className="text-left text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                <th className="px-4 py-3">Caller</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Started</th>
              </tr>
            </thead>
            <tbody>
              {recentCalls.length === 0 ? (
                <tr>
                  <td colSpan={3} className="px-4 py-12 text-center text-muted-foreground">
                    No calls yet.
                  </td>
                </tr>
              ) : (
                recentCalls.map((call) => (
                  <tr
                    key={call.id}
                    className="border-b border-border-subtle transition-smooth last:border-0 hover:bg-muted/40"
                  >
                    <td className="px-4 py-3 font-medium">
                      {call.caller_identity || "Unknown caller"}
                    </td>
                    <td className="px-4 py-3">
                      <StatusPill
                        label={call.status}
                        tone={callTone[call.status] ?? "neutral"}
                        dot={false}
                      />
                    </td>
                    <td className="px-4 py-3 text-xs text-muted-foreground">
                      {new Date(call.started_at).toLocaleString()}
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
