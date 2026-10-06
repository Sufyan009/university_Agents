import { createFileRoute } from "@tanstack/react-router";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { PageHeader } from "@/components/shared/PageHeader";
import { Search, Plus, Pencil, Trash2, X } from "lucide-react";
import { useState, useEffect } from "react";
import { formatDate } from "@/lib/format";
import {
  adminListUniversities,
  adminCreateUniversity,
  adminUpdateUniversity,
  adminDeleteUniversity,
} from "@/lib/api/admin-universities";
import type { University, UniversityPayload } from "@/lib/api/university";

export const Route = createFileRoute("/admin/universities")({
  head: () => ({
    meta: [
      { title: "Universities — Admin" },
      { name: "description", content: "Manage all tenant universities." },
    ],
  }),
  component: UniversitiesPage,
});

type ModalState =
  | { mode: "create" }
  | { mode: "edit"; university: University }
  | null;

function UniversitiesPage() {
  const qc = useQueryClient();
  const [query, setQuery] = useState("");
  const [page, setPage] = useState(1);
  const [modal, setModal] = useState<ModalState>(null);

  const PAGE_SIZE = 20;

  const { data, isLoading } = useQuery({
    queryKey: ["admin", "universities", { page, search: query }],
    queryFn: () =>
      adminListUniversities({ page, page_size: PAGE_SIZE, search: query || undefined }),
    placeholderData: (prev) => prev,
  });

  const deleteMutation = useMutation({
    mutationFn: adminDeleteUniversity,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["admin", "universities"] }),
  });

  const total = data?.total ?? 0;
  const totalPages = data?.total_pages ?? Math.ceil(total / PAGE_SIZE);

  return (
    <div className="px-4 lg:px-8 py-6 lg:py-8 max-w-[1400px] mx-auto">
      <PageHeader
        title="Universities"
        description={`${total} tenant${total === 1 ? "" : "s"}`}
        actions={
          <button
            onClick={() => setModal({ mode: "create" })}
            className="inline-flex items-center gap-2 h-9 px-3.5 rounded-md bg-gradient-primary text-primary-foreground text-sm font-semibold shadow-card hover:shadow-elevated transition-smooth"
          >
            <Plus className="h-4 w-4" />
            Add university
          </button>
        }
      />

      <div className="rounded-xl border border-border-subtle bg-surface shadow-card overflow-hidden">
        <div className="p-3 lg:p-4 border-b border-border-subtle">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <input
              value={query}
              onChange={(e) => {
                setQuery(e.target.value);
                setPage(1);
              }}
              placeholder="Search universities…"
              className="w-full h-9 pl-9 pr-3 rounded-md border border-border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring"
            />
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-surface-elevated border-b border-border-subtle">
              <tr className="text-left text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                <th className="px-4 py-3">University</th>
                <th className="px-4 py-3 hidden lg:table-cell">Phone</th>
                <th className="px-4 py-3 hidden md:table-cell">Location</th>
                <th className="px-4 py-3 hidden xl:table-cell">Website</th>
                <th className="px-4 py-3 hidden xl:table-cell">Created</th>
                <th className="px-4 py-3 text-right" />
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                Array.from({ length: 8 }).map((_, i) => (
                  <tr key={i} className="border-b border-border-subtle">
                    <td className="px-4 py-3" colSpan={6}>
                      <div className="h-8 rounded bg-muted animate-pulse" />
                    </td>
                  </tr>
                ))
              ) : (data?.items ?? []).length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-4 py-10 text-center text-muted-foreground text-sm">
                    No universities found
                  </td>
                </tr>
              ) : (
                (data?.items ?? []).map((u) => (
                  <tr
                    key={u.id}
                    className="border-b border-border-subtle last:border-0 hover:bg-muted/40 transition-smooth"
                  >
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-3">
                        <div className="h-8 w-8 rounded-md bg-primary-soft text-primary text-xs font-bold flex items-center justify-center shrink-0">
                          {u.name
                            .split(" ")
                            .map((p) => p[0])
                            .join("")
                            .slice(0, 2)
                            .toUpperCase()}
                        </div>
                        <div className="min-w-0">
                          <div className="font-medium truncate">{u.name}</div>
                          <div className="text-xs text-muted-foreground truncate">
                            {u.contact_info?.email ?? "—"}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-3 hidden lg:table-cell text-muted-foreground">
                      {u.phone ?? "—"}
                    </td>
                    <td className="px-4 py-3 hidden md:table-cell text-muted-foreground">
                      {u.location?.city ?? "—"}
                      {u.location?.country ? ` · ${u.location.country}` : ""}
                    </td>
                    <td className="px-4 py-3 hidden xl:table-cell text-muted-foreground text-xs truncate max-w-xs">
                      {u.website ?? "—"}
                    </td>
                    <td className="px-4 py-3 hidden xl:table-cell text-muted-foreground text-xs">
                      {formatDate(u.created_at)}
                    </td>
                    <td className="px-4 py-3 text-right">
                      <div className="flex items-center justify-end gap-1">
                        <button
                          onClick={() => setModal({ mode: "edit", university: u })}
                          className="p-1.5 rounded hover:bg-muted text-muted-foreground hover:text-foreground"
                          title="Edit"
                        >
                          <Pencil className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => {
                            if (confirm(`Delete ${u.name}?`)) deleteMutation.mutate(u.id);
                          }}
                          className="p-1.5 rounded hover:bg-destructive/10 text-muted-foreground hover:text-destructive"
                          title="Delete"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {totalPages > 1 && (
          <div className="px-4 py-3 border-t border-border-subtle flex items-center justify-between text-sm text-muted-foreground">
            <span>{total} total</span>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
                className="h-8 px-3 rounded-md border border-border hover:bg-muted disabled:opacity-40 disabled:cursor-not-allowed text-xs"
              >
                Prev
              </button>
              <span className="tabular-nums">
                {page} / {totalPages}
              </span>
              <button
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
                className="h-8 px-3 rounded-md border border-border hover:bg-muted disabled:opacity-40 disabled:cursor-not-allowed text-xs"
              >
                Next
              </button>
            </div>
          </div>
        )}
      </div>

      {modal && (
        <UniversityModal
          state={modal}
          onClose={() => setModal(null)}
          onSaved={() => {
            qc.invalidateQueries({ queryKey: ["admin", "universities"] });
            setModal(null);
          }}
        />
      )}
    </div>
  );
}

function emptyForm(): UniversityPayload {
  return {
    name: "",
    phone: "",
    description: "",
    website: "",
    location: { city: "", country: "" },
    contact_info: { email: "" },
    admission_office: { email: "" },
  };
}

function UniversityModal({
  state,
  onClose,
  onSaved,
}: {
  state: Exclude<ModalState, null>;
  onClose: () => void;
  onSaved: () => void;
}) {
  const isEdit = state.mode === "edit";
  const [form, setForm] = useState<UniversityPayload>(emptyForm);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (state.mode === "edit") {
      const u = state.university;
      setForm({
        name: u.name ?? "",
        phone: u.phone ?? "",
        description: u.description ?? "",
        website: u.website ?? "",
        location: { city: u.location?.city ?? "", country: u.location?.country ?? "" },
        contact_info: { email: u.contact_info?.email ?? "" },
        admission_office: { email: u.admission_office?.email ?? "" },
      });
    } else {
      setForm(emptyForm());
    }
  }, [state]);

  const buildPayload = (): UniversityPayload => ({
    name: form.name.trim(),
    ...(form.phone?.trim() && { phone: form.phone.trim() }),
    ...(form.description?.trim() && { description: form.description.trim() }),
    ...(form.website?.trim() && { website: form.website.trim() }),
    ...((form.location?.city?.trim() || form.location?.country?.trim()) && {
      location: {
        ...(form.location?.city?.trim() && { city: form.location.city.trim() }),
        ...(form.location?.country?.trim() && { country: form.location.country.trim() }),
      },
    }),
    ...(form.contact_info?.email?.trim() && {
      contact_info: { email: form.contact_info.email.trim() },
    }),
    ...(form.admission_office?.email?.trim() && {
      admission_office: { email: form.admission_office.email.trim() },
    }),
  });

  const mutation = useMutation({
    mutationFn: () =>
      isEdit
        ? adminUpdateUniversity((state as { university: University }).university.id, buildPayload())
        : adminCreateUniversity(buildPayload()),
    onSuccess: onSaved,
    onError: (err) => setError(err instanceof Error ? err.message : "An error occurred"),
  });

  const update = (field: keyof UniversityPayload, value: unknown) =>
    setForm((prev) => ({ ...prev, [field]: value as never }));

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <div className="w-full max-w-lg rounded-xl border border-border-subtle bg-surface shadow-elevated max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-5 border-b border-border-subtle">
          <h2 className="text-lg font-semibold">
            {isEdit ? "Edit university" : "Add university"}
          </h2>
          <button onClick={onClose} className="p-1.5 rounded hover:bg-muted">
            <X className="h-4 w-4 text-muted-foreground" />
          </button>
        </div>

        <div className="p-5 space-y-4">
          {error && (
            <div className="p-3 rounded-lg bg-destructive/10 border border-destructive text-destructive text-sm">
              {error}
            </div>
          )}

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <ModalField label="Name *">
              <input
                className="input"
                placeholder="e.g. Oxford University"
                value={form.name}
                onChange={(e) => update("name", e.target.value)}
              />
            </ModalField>
            <ModalField label="Phone">
              <input
                className="input"
                placeholder="+44 1865 270000"
                value={form.phone ?? ""}
                onChange={(e) => update("phone", e.target.value)}
              />
            </ModalField>
            <ModalField label="City">
              <input
                className="input"
                placeholder="Oxford"
                value={form.location?.city ?? ""}
                onChange={(e) =>
                  update("location", { ...form.location, city: e.target.value })
                }
              />
            </ModalField>
            <ModalField label="Country">
              <input
                className="input"
                placeholder="United Kingdom"
                value={form.location?.country ?? ""}
                onChange={(e) =>
                  update("location", { ...form.location, country: e.target.value })
                }
              />
            </ModalField>
            <ModalField label="Website">
              <input
                className="input"
                placeholder="https://example.edu"
                value={form.website ?? ""}
                onChange={(e) => update("website", e.target.value)}
              />
            </ModalField>
            <ModalField label="Contact email">
              <input
                className="input"
                type="email"
                placeholder="info@example.edu"
                value={form.contact_info?.email ?? ""}
                onChange={(e) => update("contact_info", { email: e.target.value })}
              />
            </ModalField>
            <ModalField label="Admissions email">
              <input
                className="input"
                type="email"
                placeholder="admissions@example.edu"
                value={form.admission_office?.email ?? ""}
                onChange={(e) => update("admission_office", { email: e.target.value })}
              />
            </ModalField>
            <div className="sm:col-span-2">
              <ModalField label="Description">
                <textarea
                  className="textarea"
                  rows={3}
                  placeholder="Tell us about this university…"
                  value={form.description ?? ""}
                  onChange={(e) => update("description", e.target.value)}
                />
              </ModalField>
            </div>
          </div>
        </div>

        <div className="flex items-center justify-end gap-2 p-5 border-t border-border-subtle">
          <button
            onClick={onClose}
            className="h-9 px-4 rounded-md border border-border bg-surface text-sm font-medium hover:bg-muted transition-smooth"
          >
            Cancel
          </button>
          <button
            onClick={() => {
              setError(null);
              if (!form.name.trim()) {
                setError("Name is required");
                return;
              }
              mutation.mutate();
            }}
            disabled={mutation.isPending}
            className="h-9 px-4 rounded-md bg-gradient-primary text-primary-foreground text-sm font-semibold shadow-card hover:shadow-elevated transition-smooth disabled:opacity-50"
          >
            {mutation.isPending ? "Saving…" : isEdit ? "Save changes" : "Create"}
          </button>
        </div>
      </div>

      <style>{`
        .input, .textarea {
          width: 100%; padding: 0.5rem 0.75rem; border-radius: 0.375rem;
          border: 1px solid var(--color-border); background: var(--color-background); font-size: 0.875rem;
          font-family: inherit;
        }
        .textarea { resize: vertical; min-height: 5rem; }
        .input:focus, .textarea:focus { outline: none; box-shadow: 0 0 0 2px var(--color-ring); border-color: transparent; }
      `}</style>
    </div>
  );
}

function ModalField({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="space-y-1.5">
      <label className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
        {label}
      </label>
      {children}
    </div>
  );
}
