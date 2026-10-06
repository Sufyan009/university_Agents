import { createFileRoute } from "@tanstack/react-router";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useState, useEffect } from "react";
import { Plus, Trash2, Save } from "lucide-react";
import { PageHeader } from "@/components/shared/PageHeader";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { usePermissions } from "@/lib/hooks/usePermissions";
import {
  getAdmissionInfo,
  upsertAdmissionInfo,
  type AdmissionInfo,
  type AdmissionPayload,
  type Deadline,
} from "@/lib/api/admissions";

export const Route = createFileRoute("/app/admissions")({
  head: () => ({
    meta: [
      { title: "Admissions — Scholaria" },
      { name: "description", content: "Manage admission criteria, eligibility, deadlines, and documents." },
    ],
  }),
  component: AdmissionsPage,
});

interface FormState {
  criteria: string;
  eligibility: string;
  application_process: string;
  scholarship_info: string;
  required_documents: string[];
  deadlines: Deadline[];
}

const EMPTY_FORM: FormState = {
  criteria: "",
  eligibility: "",
  application_process: "",
  scholarship_info: "",
  required_documents: [],
  deadlines: [],
};

function toForm(info?: AdmissionInfo | null): FormState {
  if (!info) return EMPTY_FORM;
  return {
    criteria: info.criteria ?? "",
    eligibility: info.eligibility ?? "",
    application_process: info.application_process ?? "",
    scholarship_info: info.scholarship_info ?? "",
    required_documents: info.required_documents ?? [],
    deadlines: info.deadlines ?? [],
  };
}

function AdmissionsPage() {
  const queryClient = useQueryClient();
  const { canManageAdmissions } = usePermissions();
  const canManage = canManageAdmissions();

  // 404 / errors are treated as "no record yet" -> empty form. retry:false avoids retrying 404.
  const { data, isLoading, isError } = useQuery({
    queryKey: ["admissions"],
    queryFn: getAdmissionInfo,
    retry: false,
  });

  const [form, setForm] = useState<FormState>(EMPTY_FORM);

  useEffect(() => {
    setForm(toForm(data));
  }, [data]);

  const mutation = useMutation({
    mutationFn: (payload: AdmissionPayload) => upsertAdmissionInfo(payload),
    onSuccess: (saved) => {
      queryClient.setQueryData(["admissions"], saved);
    },
  });

  const update = <K extends keyof FormState>(key: K, value: FormState[K]) =>
    setForm((f) => ({ ...f, [key]: value }));

  // required documents (string[])
  const addDocument = () => update("required_documents", [...form.required_documents, ""]);
  const setDocument = (i: number, value: string) =>
    update(
      "required_documents",
      form.required_documents.map((d, idx) => (idx === i ? value : d)),
    );
  const removeDocument = (i: number) =>
    update(
      "required_documents",
      form.required_documents.filter((_, idx) => idx !== i),
    );

  // deadlines ({label, date}[])
  const addDeadline = () => update("deadlines", [...form.deadlines, { label: "", date: "" }]);
  const setDeadline = (i: number, patch: Partial<Deadline>) =>
    update(
      "deadlines",
      form.deadlines.map((d, idx) => (idx === i ? { ...d, ...patch } : d)),
    );
  const removeDeadline = (i: number) =>
    update(
      "deadlines",
      form.deadlines.filter((_, idx) => idx !== i),
    );

  const handleSave = () => {
    const payload: AdmissionPayload = {
      criteria: form.criteria || undefined,
      eligibility: form.eligibility || undefined,
      application_process: form.application_process || undefined,
      scholarship_info: form.scholarship_info || undefined,
      required_documents: form.required_documents.filter((d) => d.trim() !== ""),
      deadlines: form.deadlines.filter((d) => (d.label?.trim() || d.date?.trim())),
    };
    mutation.mutate(payload);
  };

  if (isLoading) {
    return (
      <div className="px-4 lg:px-8 py-6 lg:py-8 max-w-[900px] mx-auto">
        <div className="text-center text-muted-foreground">Loading admissions…</div>
      </div>
    );
  }

  return (
    <div className="px-4 lg:px-8 py-6 lg:py-8 max-w-[900px] mx-auto">
      <PageHeader
        title="Admissions"
        description="Manage your university's admission criteria, eligibility, deadlines, and required documents."
        actions={
          canManage ? (
            <Button onClick={handleSave} disabled={mutation.isPending}>
              <Save className="h-4 w-4" />
              {mutation.isPending ? "Saving…" : "Save"}
            </Button>
          ) : undefined
        }
      />

      {!canManage && (
        <div className="mb-5 rounded-md border border-border bg-muted/40 px-4 py-2.5 text-sm text-muted-foreground">
          You have read-only access to admissions.
        </div>
      )}

      {isError && (
        <div className="mb-5 rounded-md border border-border bg-muted/40 px-4 py-2.5 text-sm text-muted-foreground">
          No admission record yet — fill in the form below and save to create one.
        </div>
      )}

      {mutation.isError && (
        <div className="mb-5 rounded-md border border-destructive/40 bg-destructive/10 px-4 py-2.5 text-sm text-destructive">
          {mutation.error instanceof Error ? mutation.error.message : "Failed to save admission info"}
        </div>
      )}

      {mutation.isSuccess && (
        <div className="mb-5 rounded-md border border-success/40 bg-success/10 px-4 py-2.5 text-sm text-success">
          Admission info saved.
        </div>
      )}

      <fieldset disabled={!canManage} className="space-y-6 disabled:opacity-70">
        <div className="space-y-2">
          <Label htmlFor="criteria">Admission criteria</Label>
          <Textarea
            id="criteria"
            rows={4}
            value={form.criteria}
            onChange={(e) => update("criteria", e.target.value)}
            placeholder="Describe the admission criteria…"
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="eligibility">Eligibility</Label>
          <Textarea
            id="eligibility"
            rows={4}
            value={form.eligibility}
            onChange={(e) => update("eligibility", e.target.value)}
            placeholder="Describe eligibility requirements…"
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="application_process">Application process</Label>
          <Textarea
            id="application_process"
            rows={4}
            value={form.application_process}
            onChange={(e) => update("application_process", e.target.value)}
            placeholder="Describe the step-by-step application process…"
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="scholarship_info">Scholarship info</Label>
          <Textarea
            id="scholarship_info"
            rows={4}
            value={form.scholarship_info}
            onChange={(e) => update("scholarship_info", e.target.value)}
            placeholder="General scholarship information…"
          />
        </div>

        {/* Required documents */}
        <div className="space-y-3 rounded-xl border border-border-subtle bg-surface p-4">
          <div className="flex items-center justify-between">
            <Label>Required documents</Label>
            <Button type="button" variant="outline" size="sm" onClick={addDocument}>
              <Plus className="h-4 w-4" />
              Add document
            </Button>
          </div>
          {form.required_documents.length === 0 ? (
            <p className="text-sm text-muted-foreground">No documents added yet.</p>
          ) : (
            <div className="space-y-2">
              {form.required_documents.map((doc, i) => (
                <div key={i} className="flex items-center gap-2">
                  <Input
                    value={doc}
                    onChange={(e) => setDocument(i, e.target.value)}
                    placeholder="e.g. High school transcript"
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    onClick={() => removeDocument(i)}
                    aria-label="Remove document"
                    className="text-destructive hover:bg-destructive/10"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Deadlines */}
        <div className="space-y-3 rounded-xl border border-border-subtle bg-surface p-4">
          <div className="flex items-center justify-between">
            <Label>Deadlines</Label>
            <Button type="button" variant="outline" size="sm" onClick={addDeadline}>
              <Plus className="h-4 w-4" />
              Add deadline
            </Button>
          </div>
          {form.deadlines.length === 0 ? (
            <p className="text-sm text-muted-foreground">No deadlines added yet.</p>
          ) : (
            <div className="space-y-2">
              {form.deadlines.map((d, i) => (
                <div key={i} className="flex items-center gap-2">
                  <Input
                    value={d.label ?? ""}
                    onChange={(e) => setDeadline(i, { label: e.target.value })}
                    placeholder="e.g. Fall intake"
                    className="flex-1"
                  />
                  <Input
                    type="date"
                    value={d.date ?? ""}
                    onChange={(e) => setDeadline(i, { date: e.target.value })}
                    className="w-44"
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    onClick={() => removeDeadline(i)}
                    aria-label="Remove deadline"
                    className="text-destructive hover:bg-destructive/10"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              ))}
            </div>
          )}
        </div>
      </fieldset>
    </div>
  );
}
