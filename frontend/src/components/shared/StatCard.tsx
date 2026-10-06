import { cn } from "@/lib/utils";
import { ArrowDown, ArrowUp } from "lucide-react";

interface StatCardProps {
  label: string;
  value: string;
  delta?: { value: string; positive: boolean };
  icon?: React.ComponentType<{ className?: string }>;
  accent?: "primary" | "success" | "warm" | "info" | "neutral";
  className?: string;
}

const accentMap = {
  primary: { ring: "bg-primary-soft text-primary", glow: "shadow-card" },
  success: { ring: "bg-success-soft text-success", glow: "shadow-card" },
  warm: { ring: "bg-warning-soft text-warning", glow: "shadow-card" },
  info: { ring: "bg-info-soft text-info", glow: "shadow-card" },
  neutral: { ring: "bg-muted text-muted-foreground", glow: "shadow-card" },
};

export function StatCard({ label, value, delta, icon: Icon, accent = "primary", className }: StatCardProps) {
  const a = accentMap[accent];
  return (
    <div
      className={cn(
        "group relative rounded-xl border border-border-subtle bg-surface p-5 transition-smooth hover:shadow-elevated hover:-translate-y-0.5",
        a.glow,
        className,
      )}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <div className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
            {label}
          </div>
          <div className="mt-2 text-2xl sm:text-[28px] font-bold tracking-tight tabular-nums">
            {value}
          </div>
          {delta && (
            <div
              className={cn(
                "mt-1.5 inline-flex items-center gap-1 text-xs font-medium",
                delta.positive ? "text-success" : "text-destructive",
              )}
            >
              {delta.positive ? <ArrowUp className="h-3 w-3" /> : <ArrowDown className="h-3 w-3" />}
              {delta.value}
              <span className="text-muted-foreground font-normal ml-1">vs last week</span>
            </div>
          )}
        </div>
        {Icon && (
          <div className={cn("h-10 w-10 rounded-lg flex items-center justify-center shrink-0", a.ring)}>
            <Icon className="h-5 w-5" />
          </div>
        )}
      </div>
    </div>
  );
}
