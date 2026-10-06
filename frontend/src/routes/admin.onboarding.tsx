import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { PageHeader } from "@/components/shared/PageHeader";
import {
  Check,
  ChevronRight,
  ChevronLeft,
  Building2,
  UserCog,
  Rocket,
} from "lucide-react";
import { useState } from "react";
import { adminCreateUniversity } from "@/lib/api/admin-universities";
import type { UniversityPayload } from "@/lib/api/university";
import { registerUser } from "@/lib/api/auth";

export const Route = createFileRoute("/admin/onboarding")({
  head: () => ({
    meta: [
      { title: "University Onboarding — Admin" },
      {
        name: "description",
        content: "Onboard a new university tenant: details, owner account, and go live.",
      },
    ],
  }),
  component: OnboardingPage,
});

const steps = [
  { id: 1, label: "University", Icon: Building2 },
  { id: 2, label: "Owner", Icon: UserCog },
  { id: 3, label: "Go Live", Icon: Rocket },
];

interface UniversityFormData {
  name: string;
  phone: string;
  description: string;
  website: string;
  location: { city: string; country: string };
  contact_info: { email: string; phone: string };
  admission_office: { name: string; email: string; phone: string };
}

type OwnerRole = "owner" | "admin" | "operator" | "manager";

const ROLE_OPTIONS: { value: OwnerRole; label: string }[] = [
  { value: "owner", label: "Owner" },
  { value: "admin", label: "Admin" },
  { value: "operator", label: "Operator" },
  { value: "manager", label: "Manager" },
];

interface OwnerFormData {
  email: string;
  name: string;
  phone: string;
  password: string;
  role: OwnerRole;
}

function OnboardingPage() {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [universityId, setUniversityId] = useState<string | null>(null);
  const [universitySaved, setUniversitySaved] = useState(false);
  const [ownerSaved, setOwnerSaved] = useState(false);

  const total = steps.length;

  const [university, setUniversity] = useState<UniversityFormData>({
    name: "",
    phone: "",
    description: "",
    website: "",
    location: { city: "", country: "" },
    contact_info: { email: "", phone: "" },
    admission_office: { name: "", email: "", phone: "" },
  });

  const [owner, setOwner] = useState<OwnerFormData>({
    email: "",
    name: "",
    phone: "",
    password: "",
    role: "owner",
  });

  const buildUniversityPayload = (): UniversityPayload => {
    const { name, phone, description, website, location, contact_info, admission_office } =
      university;
    return {
      name: name.trim(),
      ...(phone.trim() && { phone: phone.trim() }),
      ...(description.trim() && { description: description.trim() }),
      ...(website.trim() && { website: website.trim() }),
      ...((location.city.trim() || location.country.trim()) && {
        location: {
          ...(location.city.trim() && { city: location.city.trim() }),
          ...(location.country.trim() && { country: location.country.trim() }),
        },
      }),
      ...((contact_info.email.trim() || phone.trim()) && {
        contact_info: {
          ...(contact_info.email.trim() && { email: contact_info.email.trim() }),
          // The single university phone above is reused — we never ask for it twice.
          ...(phone.trim() && { phone: phone.trim() }),
        },
      }),
      ...((admission_office.name.trim() || admission_office.email.trim() || phone.trim()) && {
        admission_office: {
          ...(admission_office.name.trim() && { name: admission_office.name.trim() }),
          ...(admission_office.email.trim() && { email: admission_office.email.trim() }),
          ...(phone.trim() && { phone: phone.trim() }),
        },
      }),
    };
  };

  const saveUniversityIfNeeded = async () => {
    if (universitySaved && universityId) return;
    const created = await adminCreateUniversity(buildUniversityPayload());
    setUniversityId(created.id);
    setUniversitySaved(true);
  };

  const saveOwnerIfNeeded = async () => {
    if (ownerSaved) return;
    await registerUser({
      email: owner.email.trim(),
      password: owner.password,
      name: owner.name.trim() || undefined,
      phone: owner.phone.trim() || undefined,
      role: owner.role,
      university_name: university.name.trim(),
    });
    setOwnerSaved(true);
  };

  const handleContinue = async () => {
    setError(null);

    if (step === 1) {
      if (!university.name.trim()) {
        setError("University name is required");
        return;
      }
    }
    if (step === 2) {
      if (!owner.email.trim() || !owner.password) {
        setError("Owner email and password are required");
        return;
      }
    }

    try {
      setIsLoading(true);
      if (step === 1) await saveUniversityIfNeeded();
      if (step === 2) await saveOwnerIfNeeded();
      setStep((s) => Math.min(total, s + 1));
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="px-4 lg:px-8 py-6 lg:py-8 max-w-[1100px] mx-auto">
      <PageHeader
        title="Onboard a new university"
        description="Three quick steps to take a new tenant from sign-up to live."
      />

      {error && (
        <div className="mb-6 p-4 rounded-lg bg-destructive/10 border border-destructive text-destructive text-sm">
          {error}
        </div>
      )}

      {/* Stepper */}
      <div className="rounded-xl border border-border-subtle bg-surface p-4 lg:p-5 shadow-card mb-6 overflow-x-auto">
        <div className="flex items-center min-w-max gap-2">
          {steps.map((s, i) => {
            const done = step > s.id;
            const active = step === s.id;
            return (
              <div key={s.id} className="flex items-center gap-2">
                <div className="flex flex-col items-center gap-1.5">
                  <div
                    className={
                      "h-9 w-9 rounded-full flex items-center justify-center text-sm font-semibold transition-smooth " +
                      (done
                        ? "bg-success text-success-foreground"
                        : active
                          ? "bg-gradient-primary text-primary-foreground shadow-glow"
                          : "bg-muted text-muted-foreground")
                    }
                  >
                    {done ? <Check className="h-4 w-4" /> : s.id}
                  </div>
                  <span
                    className={
                      "text-xs font-medium whitespace-nowrap " +
                      (active ? "text-foreground" : "text-muted-foreground")
                    }
                  >
                    {s.label}
                  </span>
                </div>
                {i < steps.length - 1 && (
                  <div
                    className={
                      "h-0.5 w-10 lg:w-16 mb-5 transition-smooth " +
                      (step > s.id ? "bg-success" : "bg-border")
                    }
                  />
                )}
              </div>
            );
          })}
        </div>
      </div>

      <div className="rounded-xl border border-border-subtle bg-surface p-6 shadow-card min-h-[400px]">
        {step === 1 && <StepUniversity formData={university} setFormData={setUniversity} />}
        {step === 2 && <StepOwner formData={owner} setFormData={setOwner} />}
        {step === 3 && (
          <StepGoLive
            universityName={university.name}
            phone={university.phone}
            ownerEmail={owner.email}
          />
        )}
      </div>

      {/* Footer nav */}
      <div className="mt-5 flex items-center justify-between">
        <button
          onClick={() => setStep((s) => Math.max(1, s - 1))}
          disabled={step === 1}
          className="inline-flex items-center gap-2 h-10 px-4 rounded-md border border-border bg-surface text-sm font-medium hover:bg-muted disabled:opacity-40 disabled:cursor-not-allowed transition-smooth"
        >
          <ChevronLeft className="h-4 w-4" /> Back
        </button>
        <span className="text-xs text-muted-foreground tabular-nums">
          Step {step} of {total}
        </span>
        {step < total ? (
          <button
            onClick={handleContinue}
            disabled={isLoading}
            className="inline-flex items-center gap-2 h-10 px-4 rounded-md bg-gradient-primary text-primary-foreground text-sm font-semibold shadow-card hover:shadow-elevated transition-smooth disabled:opacity-50"
          >
            {isLoading ? "Saving…" : "Continue"} <ChevronRight className="h-4 w-4" />
          </button>
        ) : (
          <button
            onClick={() => navigate({ to: "/admin/universities" })}
            className="inline-flex items-center gap-2 h-10 px-4 rounded-md bg-gradient-success text-success-foreground text-sm font-semibold shadow-card hover:shadow-elevated transition-smooth"
          >
            <Rocket className="h-4 w-4" /> Go to universities
          </button>
        )}
      </div>

      <style>{`
        .input, .select, .textarea {
          width: 100%; padding: 0.5rem 0.75rem; border-radius: 0.375rem;
          border: 1px solid var(--color-border); background: var(--color-background); font-size: 0.875rem;
          font-family: inherit;
        }
        .textarea { resize: vertical; min-height: 6rem; }
        .input:focus, .select:focus, .textarea:focus { outline: none; box-shadow: 0 0 0 2px var(--color-ring); border-color: transparent; }
      `}</style>
    </div>
  );
}

function Title({ children, sub }: { children: React.ReactNode; sub?: string }) {
  return (
    <div className="mb-5">
      <h2 className="text-lg font-semibold">{children}</h2>
      {sub && <p className="text-sm text-muted-foreground mt-0.5">{sub}</p>}
    </div>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="space-y-1.5">
      <label className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
        {label}
      </label>
      {children}
    </div>
  );
}

function StepUniversity({
  formData,
  setFormData,
}: {
  formData: UniversityFormData;
  setFormData: React.Dispatch<React.SetStateAction<UniversityFormData>>;
}) {
  return (
    <>
      <Title sub="Phone is the unique tenant key for this university.">University details</Title>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <Field label="University name *">
          <input
            className="input"
            placeholder="e.g. Oxford University"
            value={formData.name}
            onChange={(e) => setFormData((p) => ({ ...p, name: e.target.value }))}
            required
          />
        </Field>
        <Field label="Phone">
          <input
            className="input"
            placeholder="+44 1865 270000"
            value={formData.phone}
            onChange={(e) => setFormData((p) => ({ ...p, phone: e.target.value }))}
          />
        </Field>
        <Field label="City">
          <input
            className="input"
            placeholder="Oxford"
            value={formData.location.city}
            onChange={(e) =>
              setFormData((p) => ({ ...p, location: { ...p.location, city: e.target.value } }))
            }
          />
        </Field>
        <Field label="Country">
          <input
            className="input"
            placeholder="United Kingdom"
            value={formData.location.country}
            onChange={(e) =>
              setFormData((p) => ({ ...p, location: { ...p.location, country: e.target.value } }))
            }
          />
        </Field>
        <Field label="Website">
          <input
            className="input"
            placeholder="https://example.edu"
            value={formData.website}
            onChange={(e) => setFormData((p) => ({ ...p, website: e.target.value }))}
          />
        </Field>
        <Field label="Contact email">
          <input
            className="input"
            type="email"
            placeholder="info@example.edu"
            value={formData.contact_info.email}
            onChange={(e) =>
              setFormData((p) => ({
                ...p,
                contact_info: { ...p.contact_info, email: e.target.value },
              }))
            }
          />
        </Field>
        <Field label="Admissions office name">
          <input
            className="input"
            placeholder="Undergraduate Admissions"
            value={formData.admission_office.name}
            onChange={(e) =>
              setFormData((p) => ({
                ...p,
                admission_office: { ...p.admission_office, name: e.target.value },
              }))
            }
          />
        </Field>
        <Field label="Admissions email">
          <input
            className="input"
            type="email"
            placeholder="admissions@example.edu"
            value={formData.admission_office.email}
            onChange={(e) =>
              setFormData((p) => ({
                ...p,
                admission_office: { ...p.admission_office, email: e.target.value },
              }))
            }
          />
        </Field>
        <div className="sm:col-span-2">
          <Field label="Description">
            <textarea
              className="textarea"
              rows={3}
              placeholder="Tell us about this university…"
              value={formData.description}
              onChange={(e) => setFormData((p) => ({ ...p, description: e.target.value }))}
            />
          </Field>
        </div>
      </div>
    </>
  );
}

function StepOwner({
  formData,
  setFormData,
}: {
  formData: OwnerFormData;
  setFormData: React.Dispatch<React.SetStateAction<OwnerFormData>>;
}) {
  return (
    <>
      <Title sub="Create the first account for this university and choose its role.">
        Owner account
      </Title>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <Field label="Email *">
          <input
            className="input"
            type="email"
            placeholder="owner@example.edu"
            value={formData.email}
            onChange={(e) => setFormData((p) => ({ ...p, email: e.target.value }))}
          />
        </Field>
        <Field label="Full name">
          <input
            className="input"
            placeholder="Jane Doe"
            value={formData.name}
            onChange={(e) => setFormData((p) => ({ ...p, name: e.target.value }))}
          />
        </Field>
        <Field label="Phone">
          <input
            className="input"
            type="tel"
            placeholder="+44 7700 900000"
            value={formData.phone}
            onChange={(e) => setFormData((p) => ({ ...p, phone: e.target.value }))}
          />
        </Field>
        <Field label="Password *">
          <input
            className="input"
            type="password"
            placeholder="Min. 8 characters"
            value={formData.password}
            onChange={(e) => setFormData((p) => ({ ...p, password: e.target.value }))}
          />
        </Field>
        <Field label="Role">
          <select
            className="select"
            value={formData.role}
            onChange={(e) =>
              setFormData((p) => ({ ...p, role: e.target.value as OwnerRole }))
            }
          >
            {ROLE_OPTIONS.map((r) => (
              <option key={r.value} value={r.value}>
                {r.label}
              </option>
            ))}
          </select>
        </Field>
      </div>
    </>
  );
}

function StepGoLive({
  universityName,
  phone,
  ownerEmail,
}: {
  universityName: string;
  phone: string;
  ownerEmail: string;
}) {
  return (
    <div className="text-center py-8">
      <div className="h-20 w-20 rounded-full bg-gradient-success mx-auto flex items-center justify-center shadow-glow">
        <Rocket className="h-10 w-10 text-success-foreground" />
      </div>
      <h2 className="mt-5 text-xl font-bold">You're all set</h2>
      <p className="mt-2 text-sm text-muted-foreground max-w-md mx-auto">
        {universityName || "The university"} has been created and its owner account is ready.
      </p>

      <div className="mt-6 mx-auto max-w-sm text-left space-y-2 rounded-lg border border-border-subtle bg-background p-4 text-sm">
        <div className="flex justify-between gap-4">
          <span className="text-muted-foreground">University</span>
          <span className="font-medium truncate">{universityName || "—"}</span>
        </div>
        <div className="flex justify-between gap-4">
          <span className="text-muted-foreground">Phone</span>
          <span className="font-medium truncate">{phone || "—"}</span>
        </div>
        <div className="flex justify-between gap-4">
          <span className="text-muted-foreground">Owner email</span>
          <span className="font-medium truncate">{ownerEmail || "—"}</span>
        </div>
      </div>

      <p className="mt-6 text-sm text-muted-foreground max-w-md mx-auto">
        The owner can now log in at{" "}
        <code className="px-1.5 py-0.5 rounded bg-muted text-foreground text-xs">/app/login</code>{" "}
        to add courses, subjects, admissions, and configure the voice agent.
      </p>

      <div className="mt-6 inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-success-soft text-success border border-success/20 text-sm font-medium">
        <Check className="h-4 w-4" /> Onboarding complete
      </div>
    </div>
  );
}
