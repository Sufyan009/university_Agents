import { createFileRoute } from "@tanstack/react-router";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { Plus, Search, Pencil, Trash2 } from "lucide-react";
import { PageHeader } from "@/components/shared/PageHeader";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { usePermissions } from "@/lib/hooks/usePermissions";
import {
  listScholarships,
  createScholarship,
  updateScholarship,
  deleteScholarship,
  type Scholarship,
  type ScholarshipPayload,
} from "@/lib/api/scholarships";

export const Route = createFileRoute("/app/scholarships")({
  head: () => ({
    meta: [
      { title: "Scholarships — Scholaria" },
      { name: "description", content: "Manage scholarships, amounts, eligibility, and deadlines." },
    ],
  }),
  component: ScholarshipsPage,
});

interface FormState {
  name: string;
  amount: string;
  eligibility: string;
  deadline: string;
  is_active: boolean;
}

const EMPTY_FORM: FormState = {
  name: "",
  amount: "",
  eligibility: "",
  deadline: "",
  is_active: true,
};

function ScholarshipsPage() {
  const queryClient = useQueryClient();
  const { canManageAdmissions } = usePermissions();
  const canManage = canManageAdmissions();

  const [query, setQuery] = useState("");
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<Scholarship | null>(null);
  const [form, setForm] = useState<FormState>(EMPTY_FORM);
  const [formError, setFormError] = useState<string | null>(null);

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ["scholarships"],
    queryFn: () => listScholarships({ page_size: 100 }),
  });

  const items = data?.items ?? [];
  const filtered = items.filter(
    (s) => query === "" || s.name.toLowerCase().includes(query.toLowerCase()),
  );

  const invalidate = () => queryClient.invalidateQueries({ queryKey: ["scholarships"] });

  const saveMutation = useMutation({
    mutationFn: (vars: { id?: string; payload: ScholarshipPayload }) =>
      vars.id ? updateScholarship(vars.id, vars.payload) : createScholarship(vars.payload),
    onSuccess: () => {
      invalidate();
      setModalOpen(false);
    },
    onError: (err) => setFormError(err instanceof Error ? err.message : "Failed to save scholarship"),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => deleteScholarship(id),
    onSuccess: invalidate,
    onError: (err) => alert(err instanceof Error ? err.message : "Failed to delete scholarship"),
  });

  const openCreate = () => {
    setEditing(null);
    setForm(EMPTY_FORM);
    setFormError(null);
    setModalOpen(true);
  };

  const openEdit = (s: Scholarship) => {
    setEditing(s);
    setForm({
      name: s.name,
      amount: s.amount ?? "",
      eligibility: s.eligibility ?? "",
      deadline: s.deadline ?? "",
      is_active: s.is_active,
    });
    setFormError(null);
    setModalOpen(true);
  };

  const handleSubmit = () => {
    if (!form.name.trim()) {
      setFormError("Name is required");
      return;
    }
    setFormError(null);
    const payload: ScholarshipPayload = {
      name: form.name.trim(),
      amount: form.amount || undefined,
      eligibility: form.eligibility || undefined,
      deadline: form.deadline || undefined,
      is_active: form.is_active,
    };
    saveMutation.mutate({ id: editing?.id, payload });
  };

  const handleDelete = (s: Scholarship) => {
    if (!confirm(`Delete scholarship "${s.name}"?`)) return;
    deleteMutation.mutate(s.id);
  };

  return (
    <div className="px-4 lg:px-8 py-6 lg:py-8 max-w-[1400px] mx-auto">
      <PageHeader
        title="Scholarships"
        description="Create and manage scholarships, eligibility, amounts, and deadlines."
        actions={
          canManage ? (
            <Button onClick={openCreate}>
              <Plus className="h-4 w-4" />
              Add scholarship
            </Button>
          ) : undefined
        }
      />

      {!canManage && (
        <div className="mb-5 rounded-md border border-border bg-muted/40 px-4 py-2.5 text-sm text-muted-foreground">
          You have read-only access to scholarships.
        </div>
      )}

      <div className="flex flex-col sm:flex-row gap-3 mb-5">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search scholarships…"
            className="h-10 pl-9"
          />
        </div>
      </div>

      {isLoading ? (
        <div className="text-center text-muted-foreground py-10">Loading scholarships…</div>
      ) : isError ? (
        <div className="text-center text-destructive py-10">
          Error: {error instanceof Error ? error.message : "Failed to load scholarships"}
        </div>
      ) : filtered.length === 0 ? (
        <div className="text-center text-muted-foreground py-10">No scholarships found.</div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map((s) => (
            <div
              key={s.id}
              className="rounded-xl border border-border-subtle bg-surface p-4 shadow-card hover:shadow-elevated transition-smooth"
            >
              <div className="flex items-start justify-between gap-2 mb-2">
                <h3 className="font-semibold truncate">{s.name}</h3>
                <Badge variant={s.is_active ? "default" : "secondary"}>
                  {s.is_active ? "Active" : "Inactive"}
                </Badge>
              </div>
              {s.amount && (
                <div className="text-sm font-medium tabular-nums mb-1">{s.amount}</div>
              )}
              {s.eligibility && (
                <p className="text-sm text-muted-foreground line-clamp-3 mb-2">{s.eligibility}</p>
              )}
              {s.deadline && (
                <div className="text-xs text-muted-foreground mb-3">Deadline: {s.deadline}</div>
              )}
              {canManage && (
                <div className="flex items-center gap-2 pt-2 border-t border-border-subtle">
                  <Button variant="outline" size="sm" onClick={() => openEdit(s)}>
                    <Pencil className="h-3.5 w-3.5" />
                    Edit
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => handleDelete(s)}
                    aria-label="Delete scholarship"
                    className="ml-auto text-destructive hover:bg-destructive/10"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      <Dialog open={modalOpen} onOpenChange={setModalOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{editing ? "Edit scholarship" : "Add scholarship"}</DialogTitle>
          </DialogHeader>

          {formError && (
            <div className="rounded-md border border-destructive/40 bg-destructive/10 px-3 py-2 text-sm text-destructive">
              {formError}
            </div>
          )}

          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="sch-name">Name *</Label>
              <Input
                id="sch-name"
                value={form.name}
                onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
                placeholder="e.g. Merit Scholarship"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="sch-amount">Amount</Label>
              <Input
                id="sch-amount"
                value={form.amount}
                onChange={(e) => setForm((f) => ({ ...f, amount: e.target.value }))}
                placeholder="e.g. $5,000 / 50% tuition"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="sch-eligibility">Eligibility</Label>
              <Textarea
                id="sch-eligibility"
                rows={3}
                value={form.eligibility}
                onChange={(e) => setForm((f) => ({ ...f, eligibility: e.target.value }))}
                placeholder="Who can apply…"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="sch-deadline">Deadline</Label>
              <Input
                id="sch-deadline"
                value={form.deadline}
                onChange={(e) => setForm((f) => ({ ...f, deadline: e.target.value }))}
                placeholder="e.g. 2026-08-31"
              />
            </div>
            <div className="flex items-center justify-between">
              <Label htmlFor="sch-active">Active</Label>
              <Switch
                id="sch-active"
                checked={form.is_active}
                onCheckedChange={(v) => setForm((f) => ({ ...f, is_active: v }))}
              />
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setModalOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleSubmit} disabled={saveMutation.isPending}>
              {saveMutation.isPending ? "Saving…" : "Save"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
