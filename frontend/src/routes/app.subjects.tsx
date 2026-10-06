import { createFileRoute } from "@tanstack/react-router";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { Plus, Trash2, Pencil, BookOpen } from "lucide-react";

import { PageHeader } from "@/components/shared/PageHeader";
import { usePermissions } from "@/lib/hooks/usePermissions";
import { listCourses } from "@/lib/api/courses";
import {
  listSubjects,
  createSubject,
  updateSubject,
  deleteSubject,
  type Subject,
  type SubjectPayload,
} from "@/lib/api/subjects";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";

export const Route = createFileRoute("/app/subjects")({
  head: () => ({
    meta: [
      { title: "Subjects — Scholaria" },
      { name: "description", content: "Manage subjects, credits, and prerequisites per course." },
    ],
  }),
  component: SubjectsPage,
});

interface SubjectFormState {
  course_id: string;
  name: string;
  credits: string;
  prerequisites: string;
  description: string;
  additional_info: string;
}

const emptyForm: SubjectFormState = {
  course_id: "",
  name: "",
  credits: "",
  prerequisites: "",
  description: "",
  additional_info: "",
};

function SubjectsPage() {
  const { canManageCourses } = usePermissions();
  const canManage = canManageCourses();
  const queryClient = useQueryClient();

  const [selectedCourse, setSelectedCourse] = useState("");
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<Subject | null>(null);
  const [form, setForm] = useState<SubjectFormState>(emptyForm);
  const [formError, setFormError] = useState<string | null>(null);

  const coursesQuery = useQuery({
    queryKey: ["courses", "all"],
    queryFn: () => listCourses({ page_size: 100 }),
  });
  const courses = coursesQuery.data?.items ?? [];

  const subjectsQuery = useQuery({
    queryKey: ["subjects", selectedCourse],
    queryFn: () => listSubjects({ course_id: selectedCourse }),
    enabled: !!selectedCourse,
  });
  const subjects = subjectsQuery.data?.items ?? [];

  const buildPayload = (): SubjectPayload => ({
    course_id: form.course_id,
    name: form.name.trim(),
    credits: form.credits.trim() ? Number(form.credits) : undefined,
    prerequisites: form.prerequisites.trim() || undefined,
    description: form.description.trim() || undefined,
    additional_info: form.additional_info.trim() || undefined,
  });

  const saveMutation = useMutation({
    mutationFn: () => {
      if (editing) {
        const { course_id: _omit, ...rest } = buildPayload();
        return updateSubject(editing.id, rest);
      }
      return createSubject(buildPayload());
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["subjects"] });
      closeModal();
    },
    onError: (err) =>
      setFormError(err instanceof Error ? err.message : "Failed to save subject"),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => deleteSubject(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["subjects"] }),
    onError: (err) => alert(err instanceof Error ? err.message : "Failed to delete subject"),
  });

  function openCreate() {
    setEditing(null);
    setForm({ ...emptyForm, course_id: selectedCourse });
    setFormError(null);
    setModalOpen(true);
  }

  function openEdit(subject: Subject) {
    setEditing(subject);
    setForm({
      course_id: subject.course_id,
      name: subject.name,
      credits: subject.credits != null ? String(subject.credits) : "",
      prerequisites: subject.prerequisites ?? "",
      description: subject.description ?? "",
      additional_info: subject.additional_info ?? "",
    });
    setFormError(null);
    setModalOpen(true);
  }

  function closeModal() {
    setModalOpen(false);
    setEditing(null);
    setForm(emptyForm);
    setFormError(null);
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setFormError(null);
    if (!form.course_id) {
      setFormError("A course is required.");
      return;
    }
    if (!form.name.trim()) {
      setFormError("Name is required.");
      return;
    }
    if (form.credits.trim() && Number.isNaN(Number(form.credits))) {
      setFormError("Credits must be a number.");
      return;
    }
    saveMutation.mutate();
  }

  function handleDelete(subject: Subject) {
    if (!confirm(`Delete subject "${subject.name}"?`)) return;
    deleteMutation.mutate(subject.id);
  }

  const courseName = (id: string) => courses.find((c) => c.id === id)?.name ?? "";

  return (
    <div className="px-4 lg:px-8 py-6 lg:py-8 max-w-[1400px] mx-auto">
      <PageHeader
        title="Subjects"
        description="Organise subjects, credits, and prerequisites under each course."
        actions={
          canManage ? (
            <button
              onClick={openCreate}
              disabled={!selectedCourse}
              className="inline-flex items-center gap-2 h-9 px-3.5 rounded-md bg-gradient-primary text-primary-foreground text-sm font-semibold shadow-card hover:shadow-elevated transition-smooth disabled:opacity-50 disabled:pointer-events-none"
            >
              <Plus className="h-4 w-4" />
              Add subject
            </button>
          ) : undefined
        }
      />

      <div className="flex flex-col sm:flex-row gap-3 mb-6">
        <select
          value={selectedCourse}
          onChange={(e) => setSelectedCourse(e.target.value)}
          className="h-10 px-3 rounded-md border border-border bg-surface text-sm focus:outline-none focus:ring-2 focus:ring-ring sm:w-80"
        >
          <option value="">Select a course…</option>
          {courses.map((c) => (
            <option key={c.id} value={c.id}>
              {c.name}
            </option>
          ))}
        </select>
      </div>

      {coursesQuery.isError ? (
        <div className="text-center text-destructive py-12">
          Error loading courses:{" "}
          {coursesQuery.error instanceof Error ? coursesQuery.error.message : "Failed"}
        </div>
      ) : !selectedCourse ? (
        <div className="text-center text-muted-foreground py-12">
          Select a course to view its subjects.
        </div>
      ) : subjectsQuery.isLoading ? (
        <div className="text-center text-muted-foreground py-12">Loading subjects…</div>
      ) : subjectsQuery.isError ? (
        <div className="text-center text-destructive py-12">
          Error:{" "}
          {subjectsQuery.error instanceof Error
            ? subjectsQuery.error.message
            : "Failed to load subjects"}
        </div>
      ) : subjects.length === 0 ? (
        <div className="text-center text-muted-foreground py-12">
          No subjects in this course yet.
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {subjects.map((subject) => (
            <div
              key={subject.id}
              className="rounded-xl border border-border-subtle bg-surface p-4 shadow-card hover:shadow-elevated transition-smooth flex flex-col"
            >
              <div className="flex items-start justify-between gap-2 mb-1">
                <h3 className="font-semibold truncate">{subject.name}</h3>
                <BookOpen className="h-4 w-4 text-muted-foreground shrink-0" />
              </div>
              <div className="flex flex-wrap gap-1.5 mb-3 text-xs text-muted-foreground">
                {subject.credits != null && (
                  <span className="px-2 py-0.5 rounded-full bg-primary-soft text-primary font-medium">
                    {subject.credits} credits
                  </span>
                )}
                {subject.prerequisites && (
                  <span className="px-2 py-0.5 rounded-full bg-muted">Has prerequisites</span>
                )}
              </div>
              <p className="text-sm text-muted-foreground line-clamp-3 mb-4 min-h-[3.75rem] flex-1">
                {subject.description || "No description."}
              </p>
              {canManage && (
                <div className="flex items-center justify-end gap-1 border-t border-border-subtle pt-3">
                  <button
                    onClick={() => openEdit(subject)}
                    className="p-1.5 text-muted-foreground hover:bg-muted rounded-md transition-smooth"
                    aria-label="Edit subject"
                  >
                    <Pencil className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => handleDelete(subject)}
                    className="p-1.5 text-destructive hover:bg-destructive/10 rounded-md transition-smooth"
                    aria-label="Delete subject"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      <Dialog open={modalOpen} onOpenChange={(o) => (o ? setModalOpen(true) : closeModal())}>
        <DialogContent className="max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>{editing ? "Edit subject" : "Add subject"}</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-1.5">
              <Label htmlFor="subject-course">Course *</Label>
              {editing ? (
                <Input id="subject-course" value={courseName(form.course_id)} disabled />
              ) : (
                <select
                  id="subject-course"
                  value={form.course_id}
                  onChange={(e) => setForm((f) => ({ ...f, course_id: e.target.value }))}
                  className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                  required
                >
                  <option value="">Select a course…</option>
                  {courses.map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.name}
                    </option>
                  ))}
                </select>
              )}
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <Label htmlFor="subject-name">Name *</Label>
                <Input
                  id="subject-name"
                  value={form.name}
                  onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
                  placeholder="e.g. Algorithms"
                  required
                />
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="subject-credits">Credits</Label>
                <Input
                  id="subject-credits"
                  type="number"
                  min={0}
                  value={form.credits}
                  onChange={(e) => setForm((f) => ({ ...f, credits: e.target.value }))}
                  placeholder="e.g. 3"
                />
              </div>
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="subject-prereq">Prerequisites</Label>
              <Textarea
                id="subject-prereq"
                value={form.prerequisites}
                onChange={(e) => setForm((f) => ({ ...f, prerequisites: e.target.value }))}
                rows={2}
              />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="subject-description">Description</Label>
              <Textarea
                id="subject-description"
                value={form.description}
                onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
                rows={3}
              />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="subject-info">Additional info</Label>
              <Textarea
                id="subject-info"
                value={form.additional_info}
                onChange={(e) => setForm((f) => ({ ...f, additional_info: e.target.value }))}
                rows={2}
              />
            </div>
            {formError && <p className="text-sm text-destructive">{formError}</p>}
            <DialogFooter>
              <Button type="button" variant="outline" onClick={closeModal}>
                Cancel
              </Button>
              <Button type="submit" disabled={saveMutation.isPending}>
                {saveMutation.isPending ? "Saving…" : editing ? "Save changes" : "Create subject"}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}
