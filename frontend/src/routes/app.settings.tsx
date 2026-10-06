import { createFileRoute } from "@tanstack/react-router";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { Building2, User as UserIcon, KeyRound } from "lucide-react";

import { PageHeader } from "@/components/shared/PageHeader";
import {
  getUniversityProfile,
  updateUniversityProfile,
  type UniversityPayload,
} from "@/lib/api/university";
import { getUserProfile, updateUserProfile, changeUserPassword } from "@/lib/api/auth";

export const Route = createFileRoute("/app/settings")({
  head: () => ({ meta: [{ title: "Settings — Scholaria" }] }),
  component: SettingsPage,
});

type Tab = "university" | "profile";

function SettingsPage() {
  const [tab, setTab] = useState<Tab>("university");

  return (
    <div className="mx-auto max-w-[900px] px-4 py-6 lg:px-8 lg:py-8">
      <PageHeader title="Settings" description="Manage your university profile and your account." />

      <div className="mb-6 flex gap-1 rounded-lg border border-border-subtle bg-surface p-1">
        <TabButton active={tab === "university"} onClick={() => setTab("university")} icon={Building2} label="University" />
        <TabButton active={tab === "profile"} onClick={() => setTab("profile")} icon={UserIcon} label="My Profile" />
      </div>

      {tab === "university" ? <UniversitySection /> : <ProfileSection />}
    </div>
  );
}

function TabButton({
  active,
  onClick,
  icon: Icon,
  label,
}: {
  active: boolean;
  onClick: () => void;
  icon: React.ComponentType<{ className?: string }>;
  label: string;
}) {
  return (
    <button
      onClick={onClick}
      className={
        "flex-1 inline-flex items-center justify-center gap-2 rounded-md px-3 py-2 text-sm font-medium transition-smooth " +
        (active ? "bg-gradient-primary text-primary-foreground shadow-glow" : "text-muted-foreground hover:bg-muted")
      }
    >
      <Icon className="h-4 w-4" />
      {label}
    </button>
  );
}

const inputCls =
  "w-full rounded-md border border-border bg-background px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-smooth";

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <label className="mb-1.5 block text-sm font-medium">{label}</label>
      {children}
    </div>
  );
}

function Card({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="rounded-xl border border-border-subtle bg-surface p-6 shadow-card">
      <h3 className="mb-4 font-semibold">{title}</h3>
      {children}
    </div>
  );
}

function UniversitySection() {
  const qc = useQueryClient();
  const { data, isLoading, error } = useQuery({
    queryKey: ["university", "profile"],
    queryFn: getUniversityProfile,
    retry: false,
  });

  const [form, setForm] = useState<UniversityPayload>({ name: "" });
  const [msg, setMsg] = useState<string | null>(null);

  useEffect(() => {
    if (data) {
      setForm({
        name: data.name ?? "",
        description: data.description ?? "",
        phone: data.phone ?? "",
        website: data.website ?? "",
        location: data.location ?? {},
        contact_info: data.contact_info ?? {},
        admission_office: data.admission_office ?? {},
      });
    }
  }, [data]);

  const mutation = useMutation({
    mutationFn: (payload: Partial<UniversityPayload>) => updateUniversityProfile(payload),
    onSuccess: () => {
      setMsg("Saved.");
      qc.invalidateQueries({ queryKey: ["university", "profile"] });
    },
    onError: (e) => setMsg(e instanceof Error ? e.message : "Save failed"),
  });

  if (isLoading) return <Card title="University profile">Loading…</Card>;

  return (
    <Card title="University profile">
      {error && (
        <p className="mb-4 rounded-md bg-warning-soft px-3 py-2 text-sm text-warning-foreground">
          No profile found yet — fill this in and save to create it.
        </p>
      )}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <Field label="Name">
          <input className={inputCls} value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
        </Field>
        <Field label="Phone (tenant number)">
          <input className={inputCls} value={form.phone ?? ""} onChange={(e) => setForm({ ...form, phone: e.target.value })} />
        </Field>
        <Field label="Website">
          <input className={inputCls} value={form.website ?? ""} onChange={(e) => setForm({ ...form, website: e.target.value })} />
        </Field>
        <Field label="City">
          <input
            className={inputCls}
            value={form.location?.city ?? ""}
            onChange={(e) => setForm({ ...form, location: { ...form.location, city: e.target.value } })}
          />
        </Field>
        <Field label="Country">
          <input
            className={inputCls}
            value={form.location?.country ?? ""}
            onChange={(e) => setForm({ ...form, location: { ...form.location, country: e.target.value } })}
          />
        </Field>
        <Field label="Contact email">
          <input
            className={inputCls}
            value={form.contact_info?.email ?? ""}
            onChange={(e) => setForm({ ...form, contact_info: { ...form.contact_info, email: e.target.value } })}
          />
        </Field>
        <Field label="Admissions office email">
          <input
            className={inputCls}
            value={form.admission_office?.email ?? ""}
            onChange={(e) => setForm({ ...form, admission_office: { ...form.admission_office, email: e.target.value } })}
          />
        </Field>
        <Field label="Admissions office phone">
          <input
            className={inputCls}
            value={form.admission_office?.phone ?? ""}
            onChange={(e) => setForm({ ...form, admission_office: { ...form.admission_office, phone: e.target.value } })}
          />
        </Field>
      </div>
      <div className="mt-4">
        <Field label="Description">
          <textarea
            className={inputCls + " min-h-[90px]"}
            value={form.description ?? ""}
            onChange={(e) => setForm({ ...form, description: e.target.value })}
          />
        </Field>
      </div>

      {msg && <p className="mt-4 text-sm text-muted-foreground">{msg}</p>}

      <div className="mt-5">
        <button
          onClick={() => {
            setMsg(null);
            mutation.mutate(form);
          }}
          disabled={mutation.isPending}
          className="rounded-lg bg-gradient-primary px-5 py-2.5 text-sm font-semibold text-primary-foreground shadow-glow transition-smooth hover:shadow-elevated disabled:opacity-60"
        >
          {mutation.isPending ? "Saving…" : "Save university"}
        </button>
      </div>
    </Card>
  );
}

function ProfileSection() {
  const { data } = useQuery({ queryKey: ["me"], queryFn: getUserProfile, retry: false });

  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");
  const [profileMsg, setProfileMsg] = useState<string | null>(null);

  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [pwMsg, setPwMsg] = useState<string | null>(null);

  useEffect(() => {
    if (data) {
      setName(data.name ?? "");
      setPhone(data.phone ?? "");
    }
  }, [data]);

  const profileMut = useMutation({
    mutationFn: () => updateUserProfile({ name, phone }),
    onSuccess: () => setProfileMsg("Saved."),
    onError: (e) => setProfileMsg(e instanceof Error ? e.message : "Save failed"),
  });

  const pwMut = useMutation({
    mutationFn: () => changeUserPassword({ current_password: currentPassword, new_password: newPassword }),
    onSuccess: () => {
      setPwMsg("Password changed.");
      setCurrentPassword("");
      setNewPassword("");
    },
    onError: (e) => setPwMsg(e instanceof Error ? e.message : "Change failed"),
  });

  return (
    <div className="space-y-6">
      <Card title="My profile">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <Field label="Name">
            <input className={inputCls} value={name} onChange={(e) => setName(e.target.value)} />
          </Field>
          <Field label="Phone">
            <input className={inputCls} value={phone} onChange={(e) => setPhone(e.target.value)} />
          </Field>
        </div>
        {profileMsg && <p className="mt-4 text-sm text-muted-foreground">{profileMsg}</p>}
        <div className="mt-5">
          <button
            onClick={() => {
              setProfileMsg(null);
              profileMut.mutate();
            }}
            disabled={profileMut.isPending}
            className="rounded-lg bg-gradient-primary px-5 py-2.5 text-sm font-semibold text-primary-foreground shadow-glow transition-smooth hover:shadow-elevated disabled:opacity-60"
          >
            {profileMut.isPending ? "Saving…" : "Save profile"}
          </button>
        </div>
      </Card>

      <Card title="Change password">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <Field label="Current password">
            <input type="password" className={inputCls} value={currentPassword} onChange={(e) => setCurrentPassword(e.target.value)} />
          </Field>
          <Field label="New password">
            <input type="password" className={inputCls} value={newPassword} onChange={(e) => setNewPassword(e.target.value)} />
          </Field>
        </div>
        {pwMsg && <p className="mt-4 text-sm text-muted-foreground">{pwMsg}</p>}
        <div className="mt-5">
          <button
            onClick={() => {
              setPwMsg(null);
              pwMut.mutate();
            }}
            disabled={pwMut.isPending || !currentPassword || !newPassword}
            className="inline-flex items-center gap-2 rounded-lg border border-border bg-background px-5 py-2.5 text-sm font-semibold transition-smooth hover:bg-muted disabled:opacity-60"
          >
            <KeyRound className="h-4 w-4" />
            {pwMut.isPending ? "Updating…" : "Update password"}
          </button>
        </div>
      </Card>
    </div>
  );
}
