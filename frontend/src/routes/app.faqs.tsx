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
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { usePermissions } from "@/lib/hooks/usePermissions";
import {
  listFaqs,
  createFaq,
  updateFaq,
  deleteFaq,
  type FAQ,
  type FAQPayload,
} from "@/lib/api/faqs";

export const Route = createFileRoute("/app/faqs")({
  head: () => ({
    meta: [
      { title: "FAQs — Scholaria" },
      { name: "description", content: "Manage frequently asked questions and answers." },
    ],
  }),
  component: FaqsPage,
});

interface FormState {
  question: string;
  answer: string;
  category: string;
  is_active: boolean;
}

const EMPTY_FORM: FormState = {
  question: "",
  answer: "",
  category: "",
  is_active: true,
};

function FaqsPage() {
  const queryClient = useQueryClient();
  const { canManageKnowledge } = usePermissions();
  const canManage = canManageKnowledge();

  const [query, setQuery] = useState("");
  const [activeCategory, setActiveCategory] = useState("All");
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<FAQ | null>(null);
  const [form, setForm] = useState<FormState>(EMPTY_FORM);
  const [formError, setFormError] = useState<string | null>(null);

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ["faqs"],
    queryFn: () => listFaqs({ page_size: 100 }),
  });

  const items = data?.items ?? [];
  const categories = ["All", ...Array.from(new Set(items.map((f) => f.category).filter(Boolean) as string[]))];

  const filtered = items.filter(
    (f) =>
      (activeCategory === "All" || f.category === activeCategory) &&
      (query === "" ||
        f.question.toLowerCase().includes(query.toLowerCase()) ||
        f.answer.toLowerCase().includes(query.toLowerCase())),
  );

  const invalidate = () => queryClient.invalidateQueries({ queryKey: ["faqs"] });

  const saveMutation = useMutation({
    mutationFn: (vars: { id?: string; payload: FAQPayload }) =>
      vars.id ? updateFaq(vars.id, vars.payload) : createFaq(vars.payload),
    onSuccess: () => {
      invalidate();
      setModalOpen(false);
    },
    onError: (err) => setFormError(err instanceof Error ? err.message : "Failed to save FAQ"),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => deleteFaq(id),
    onSuccess: invalidate,
    onError: (err) => alert(err instanceof Error ? err.message : "Failed to delete FAQ"),
  });

  const openCreate = () => {
    setEditing(null);
    setForm(EMPTY_FORM);
    setFormError(null);
    setModalOpen(true);
  };

  const openEdit = (f: FAQ) => {
    setEditing(f);
    setForm({
      question: f.question,
      answer: f.answer,
      category: f.category ?? "",
      is_active: f.is_active,
    });
    setFormError(null);
    setModalOpen(true);
  };

  const handleSubmit = () => {
    if (!form.question.trim()) {
      setFormError("Question is required");
      return;
    }
    if (!form.answer.trim()) {
      setFormError("Answer is required");
      return;
    }
    setFormError(null);
    const payload: FAQPayload = {
      question: form.question.trim(),
      answer: form.answer.trim(),
      category: form.category || undefined,
      is_active: form.is_active,
    };
    saveMutation.mutate({ id: editing?.id, payload });
  };

  const handleDelete = (f: FAQ) => {
    if (!confirm("Delete this FAQ?")) return;
    deleteMutation.mutate(f.id);
  };

  return (
    <div className="px-4 lg:px-8 py-6 lg:py-8 max-w-[1000px] mx-auto">
      <PageHeader
        title="FAQs"
        description="Manage frequently asked questions students ask the voice agent."
        actions={
          canManage ? (
            <Button onClick={openCreate}>
              <Plus className="h-4 w-4" />
              Add FAQ
            </Button>
          ) : undefined
        }
      />

      {!canManage && (
        <div className="mb-5 rounded-md border border-border bg-muted/40 px-4 py-2.5 text-sm text-muted-foreground">
          You have read-only access to FAQs.
        </div>
      )}

      <div className="flex flex-col sm:flex-row gap-3 mb-5">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search FAQs…"
            className="h-10 pl-9"
          />
        </div>
      </div>

      {/* Category tabs */}
      {categories.length > 1 && (
        <div className="flex flex-wrap gap-1.5 mb-6 border-b border-border-subtle pb-3">
          {categories.map((c) => (
            <button
              key={c}
              onClick={() => setActiveCategory(c)}
              className={
                "px-3.5 py-1.5 rounded-full text-sm font-medium transition-smooth " +
                (activeCategory === c
                  ? "bg-primary-soft text-primary"
                  : "text-muted-foreground hover:bg-muted hover:text-foreground")
              }
            >
              {c}
            </button>
          ))}
        </div>
      )}

      {isLoading ? (
        <div className="text-center text-muted-foreground py-10">Loading FAQs…</div>
      ) : isError ? (
        <div className="text-center text-destructive py-10">
          Error: {error instanceof Error ? error.message : "Failed to load FAQs"}
        </div>
      ) : filtered.length === 0 ? (
        <div className="text-center text-muted-foreground py-10">No FAQs found.</div>
      ) : (
        <Accordion type="multiple" className="space-y-2">
          {filtered.map((f) => (
            <AccordionItem
              key={f.id}
              value={f.id}
              className="rounded-xl border border-border-subtle bg-surface px-4"
            >
              <AccordionTrigger className="text-left">
                <span className="flex flex-1 items-center gap-2 pr-2">
                  <span className="font-medium">{f.question}</span>
                  {f.category && (
                    <Badge variant="secondary" className="shrink-0">
                      {f.category}
                    </Badge>
                  )}
                  {!f.is_active && (
                    <Badge variant="outline" className="shrink-0">
                      Inactive
                    </Badge>
                  )}
                </span>
              </AccordionTrigger>
              <AccordionContent>
                <p className="whitespace-pre-wrap text-sm text-muted-foreground">{f.answer}</p>
                {canManage && (
                  <div className="flex items-center gap-2 pt-4 mt-2 border-t border-border-subtle">
                    <Button variant="outline" size="sm" onClick={() => openEdit(f)}>
                      <Pencil className="h-3.5 w-3.5" />
                      Edit
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => handleDelete(f)}
                      aria-label="Delete FAQ"
                      className="ml-auto text-destructive hover:bg-destructive/10"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                )}
              </AccordionContent>
            </AccordionItem>
          ))}
        </Accordion>
      )}

      <Dialog open={modalOpen} onOpenChange={setModalOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{editing ? "Edit FAQ" : "Add FAQ"}</DialogTitle>
          </DialogHeader>

          {formError && (
            <div className="rounded-md border border-destructive/40 bg-destructive/10 px-3 py-2 text-sm text-destructive">
              {formError}
            </div>
          )}

          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="faq-question">Question *</Label>
              <Input
                id="faq-question"
                value={form.question}
                onChange={(e) => setForm((f) => ({ ...f, question: e.target.value }))}
                placeholder="e.g. What is the application deadline?"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="faq-answer">Answer *</Label>
              <Textarea
                id="faq-answer"
                rows={5}
                value={form.answer}
                onChange={(e) => setForm((f) => ({ ...f, answer: e.target.value }))}
                placeholder="Provide the answer…"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="faq-category">Category</Label>
              <Input
                id="faq-category"
                value={form.category}
                onChange={(e) => setForm((f) => ({ ...f, category: e.target.value }))}
                placeholder="e.g. Admissions"
              />
            </div>
            <div className="flex items-center justify-between">
              <Label htmlFor="faq-active">Active</Label>
              <Switch
                id="faq-active"
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
