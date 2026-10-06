import { cn } from "@/lib/utils";

type Tone = "success" | "warning" | "info" | "danger" | "neutral" | "primary";

const toneMap: Record<Tone, string> = {
  success: "bg-success-soft text-success border-success/20",
  warning: "bg-warning-soft text-warning-foreground border-warning/30",
  info: "bg-info-soft text-info border-info/20",
  danger: "bg-danger-soft text-destructive border-destructive/20",
  neutral: "bg-muted text-muted-foreground border-border",
  primary: "bg-primary-soft text-primary border-primary/20",
};

export function StatusPill({
  label,
  tone = "neutral",
  className,
  dot = true,
}: {
  label: string;
  tone?: Tone;
  className?: string;
  dot?: boolean;
}) {
  const dotColor: Record<Tone, string> = {
    success: "bg-success",
    warning: "bg-warning",
    info: "bg-info",
    danger: "bg-destructive",
    neutral: "bg-muted-foreground",
    primary: "bg-primary",
  };
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full border text-xs font-medium whitespace-nowrap",
        toneMap[tone],
        className,
      )}
    >
      {dot && <span className={cn("h-1.5 w-1.5 rounded-full", dotColor[tone])} />}
      {label}
    </span>
  );
}

// Specific helpers
export function OrderStatusPill({ status }: { status: string }) {
  const map: Record<string, { label: string; tone: Tone }> = {
    pending: { label: "Pending", tone: "warning" },
    confirmed: { label: "Confirmed", tone: "info" },
    preparing: { label: "Preparing", tone: "info" },
    out_for_delivery: { label: "Out for Delivery", tone: "primary" },
    completed: { label: "Completed", tone: "success" },
    cancelled: { label: "Cancelled", tone: "danger" },
  };
  const cfg = map[status] ?? { label: status, tone: "neutral" as Tone };
  return <StatusPill label={cfg.label} tone={cfg.tone} />;
}

export function PaymentStatusPill({ status }: { status: string }) {
  const map: Record<string, { label: string; tone: Tone }> = {
    paid: { label: "Paid", tone: "success" },
    pending: { label: "Pending", tone: "warning" },
    failed: { label: "Failed", tone: "danger" },
    refunded: { label: "Refunded", tone: "neutral" },
  };
  const cfg = map[status] ?? { label: status, tone: "neutral" as Tone };
  return <StatusPill label={cfg.label} tone={cfg.tone} />;
}
