import { format, formatDistanceToNow } from "date-fns";

export const currency = (n: number, code = "USD") =>
  new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: code,
    maximumFractionDigits: 0,
  }).format(n);

export const currencyExact = (n: number, code = "USD") =>
  new Intl.NumberFormat("en-US", { style: "currency", currency: code }).format(n);

export const compactNumber = (n: number) =>
  new Intl.NumberFormat("en-US", { notation: "compact", maximumFractionDigits: 1 }).format(n);

// Naive UTC strings from the API lack "Z"; append it so JS treats them as UTC not local
const utc = (iso: string) => (iso.endsWith("Z") || iso.includes("+") ? iso : iso + "Z");

export const formatDate = (iso: string, fmt = "MMM d, yyyy") => format(new Date(utc(iso)), fmt);

export const formatDateTime = (iso: string) => format(new Date(utc(iso)), "MMM d, yyyy · h:mm a");

export const relativeTime = (iso: string) =>
  formatDistanceToNow(new Date(utc(iso)), { addSuffix: true });

export const formatDuration = (sec: number) => {
  const m = Math.floor(sec / 60);
  const s = sec % 60;
  return `${m}m ${String(s).padStart(2, "0")}s`;
};
