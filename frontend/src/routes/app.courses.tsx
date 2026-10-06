import { createFileRoute } from "@tanstack/react-router";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { Plus, Search, Trash2, Pencil, GraduationCap } from "lucide-react";

import { PageHeader } from "@/components/shared/PageHeader";
import { usePermissions } from "@/lib/hooks/usePermissions";
import {
  listCourses,
  createCourse,
  updateCourse,
  deleteCourse,
  type Course,
  type CoursePayload,
} from "@/lib/api/courses";
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

export const Route = createFileRoute("/app/courses")({
  head: () => ({
    meta: [
      { title: "Courses — Scholaria" },
      { name: "description", content: "Manage courses, degree types, fees, and admission requirements." },
    ],
  }),
  component: CoursesPage,
});

interface CourseFormState {
  name: string;
  degree_type: string;
  duration: string;
  description: string;
  admission_requirements: string;
  fee_summary: string;
}

const emptyForm: CourseFormState = {
  name: "",
  degree_type: "",
  duration: "",
  description: "",
  admission_requirements: "",
  fee_summary: "",
};

// Degree type → typical duration options. Duration dropdown is driven by the
// selected degree type (e.g. undergrad is usually 3–4 years, a Master's 1–2).
const DEGREE_DURATIONS: Record<string, string[]> = {
  "Foundation": ["6 months", "1 year"],
  "Diploma": ["6 months", "1 year", "2 years"],
  "Undergraduate": ["3 years", "4 years", "5 years"],
  "Postgraduate (Master's)": ["1 year", "2 years"],
  "PhD / Doctorate": ["3 years", "4 years", "5 years", "6 years"],
  "Postdoctoral": ["1 year", "2 years", "3 years"],
};
const DEGREE_TYPES = Object.keys(DEGREE_DURATIONS);
const ALL_DURATIONS = Array.from(new Set(Object.values(DEGREE_DURATIONS).flat()));

const selectClass =
  "flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50";

function feeSummaryFrom(fee?: Record<string, unknown>): string {
  if (!fee) return "";
  if (typeof fee.summary === "string") return fee.summary;
  try {
    return JSON.stringify(fee);
  } catch {
    return "";
  }
}

function CoursesPage() {
  const { canManageCourses } = usePermissions();
  const canManage = canManageCourses();
  const queryClient = useQueryClient();

  const [search, setSearch] = useState("");
  const [degreeFilter, setDegreeFilter] = useState("");
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<Course | null>(null);
  const [form, setForm] = useState<CourseFormState>(emptyForm);
  const [formError, setFormError] = useState<string | null>(null);

  const queryParams = {
    search: search || undefined,
    degree_type: degreeFilter || undefined,
  };

  const { data, isLoading, error } = useQuery({
    queryKey: ["courses", queryParams],
    queryFn: () => listCourses(queryParams),
  });

  const courses = data?.items ?? [];
  const degreeTypes = Array.from(
    new Set(courses.map((c) => c.degree_type).filter((d): d is string => !!d)),
  );

  const buildPayload = (): CoursePayload => ({
    name: form.name.trim(),
    degree_type: form.degree_type.trim() || undefined,
    duration: form.duration.trim() || undefined,
    description: form.description.trim() || undefined,
    admission_requirements: form.admission_requirements.trim() || undefined,
    fee_structure: form.fee_summary.trim() ? { summary: form.fee_summary.trim() } : undefined,
  });

  const saveMutation = useMutation({
    mutationFn: () =>
      editing ? updateCourse(editing.id, buildPayload()) : createCourse(buildPayload()),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["courses"] });
      closeModal();
    },
    onError: (err) =>
      setFormError(err instanceof Error ? err.message : "Failed to save course"),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => deleteCourse(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["courses"] }),
    onError: (err) => alert(err instanceof Error ? err.message : "Failed to delete course"),
  });

  function openCreate() {
    setEditing(null);
    setForm(emptyForm);
    setFormError(null);
    setModalOpen(true);
  }

  function openEdit(course: Course) {
    setEditing(course);
    setForm({
      name: course.name,
      degree_type: course.degree_type ?? "",
      duration: course.duration ?? "",
      description: course.description ?? "",
      admission_requirements: course.admission_requirements ?? "",
      fee_summary: feeSummaryFrom(course.fee_structure),
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
    if (!form.name.trim()) {
      setFormError("Name is required.");
      return;
    }
    saveMutation.mutate();
  }

  function handleDelete(course: Course) {
    if (!confirm(`Delete course "${course.name}"?`)) return;
    deleteMutation.mutate(course.id);
  }

  return (
    <div className="px-4 lg:px-8 py-6 lg:py-8 max-w-[1400px] mx-auto">
      <PageHeader
        title="Courses"
        description="Manage your course catalogue, degree types, fees, and admission requirements."
        actions={
          canManage ? (
            <button
              onClick={openCreate}
              className="inline-flex items-center gap-2 h-9 px-3.5 rounded-md bg-gradient-primary text-primary-foreground text-sm font-semibold shadow-card hover:shadow-elevated transition-smooth"
            >
              <Plus className="h-4 w-4" />
              Add course
            </button>
          ) : undefined
        }
      />

      <div className="flex flex-col sm:flex-row gap-3 mb-6">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search courses…"
            className="w-full h-10 pl-9 pr-3 rounded-md border border-border bg-surface text-sm focus:outline-none focus:ring-2 focus:ring-ring"
          />
        </div>
        <select
          value={degreeFilter}
          onChange={(e) => setDegreeFilter(e.target.value)}
          className="h-10 px-3 rounded-md border border-border bg-surface text-sm focus:outline-none focus:ring-2 focus:ring-ring sm:w-56"
        >
          <option value="">All degree types</option>
          {degreeTypes.map((d) => (
            <option key={d} value={d}>
              {d}
            </option>
          ))}
        </select>
      </div>

      {isLoading ? (
        <div className="text-center text-muted-foreground py-12">Loading courses…</div>
      ) : error ? (
        <div className="text-center text-destructive py-12">
          Error: {error instanceof Error ? error.message : "Failed to load courses"}
        </div>
      ) : courses.length === 0 ? (
        <div className="text-center text-muted-foreground py-12">No courses found.</div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {courses.map((course) => (
            <div
              key={course.id}
              className="rounded-xl border border-border-subtle bg-surface p-4 shadow-card hover:shadow-elevated transition-smooth flex flex-col"
            >
              <div className="flex items-start justify-between gap-2 mb-1">
                <h3 className="font-semibold truncate">{course.name}</h3>
                <GraduationCap className="h-4 w-4 text-muted-foreground shrink-0" />
              </div>
              <div className="flex flex-wrap gap-1.5 mb-3 text-xs text-muted-foreground">
                {course.degree_type && (
                  <span className="px-2 py-0.5 rounded-full bg-primary-soft text-primary font-medium">
                    {course.degree_type}
                  </span>
                )}
                {course.duration && (
                  <span className="px-2 py-0.5 rounded-full bg-muted">{course.duration}</span>
                )}
              </div>
              <p className="text-sm text-muted-foreground line-clamp-3 mb-4 min-h-[3.75rem] flex-1">
                {course.description || "No description."}
              </p>
              {canManage && (
                <div className="flex items-center justify-end gap-1 border-t border-border-subtle pt-3">
                  <button
                    onClick={() => openEdit(course)}
                    className="p-1.5 text-muted-foreground hover:bg-muted rounded-md transition-smooth"
                    aria-label="Edit course"
                  >
                    <Pencil className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => handleDelete(course)}
                    className="p-1.5 text-destructive hover:bg-destructive/10 rounded-md transition-smooth"
                    aria-label="Delete course"
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
            <DialogTitle>{editing ? "Edit course" : "Add course"}</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-1.5">
              <Label htmlFor="course-name">Name *</Label>
              <Input
                id="course-name"
                value={form.name}
                onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
                placeholder="e.g. Computer Science"
                required
              />
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <Label htmlFor="course-degree">Degree type</Label>
                <select
                  id="course-degree"
                  className={selectClass}
                  value={form.degree_type}
                  onChange={(e) =>
                    // Changing the degree type resets the duration so it can only
                    // hold a value valid for the newly-selected degree.
                    setForm((f) => ({ ...f, degree_type: e.target.value, duration: "" }))
                  }
                >
                  <option value="">Select degree type…</option>
                  {DEGREE_TYPES.map((d) => (
                    <option key={d} value={d}>
                      {d}
                    </option>
                  ))}
                  {form.degree_type && !DEGREE_TYPES.includes(form.degree_type) && (
                    <option value={form.degree_type}>{form.degree_type}</option>
                  )}
                </select>
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="course-duration">Duration</Label>
                <select
                  id="course-duration"
                  className={selectClass}
                  value={form.duration}
                  onChange={(e) => setForm((f) => ({ ...f, duration: e.target.value }))}
                  disabled={!form.degree_type}
                >
                  <option value="">
                    {form.degree_type ? "Select duration…" : "Select a degree type first"}
                  </option>
                  {(DEGREE_DURATIONS[form.degree_type] ?? ALL_DURATIONS).map((d) => (
                    <option key={d} value={d}>
                      {d}
                    </option>
                  ))}
                  {form.duration &&
                    !(DEGREE_DURATIONS[form.degree_type] ?? ALL_DURATIONS).includes(
                      form.duration,
                    ) && <option value={form.duration}>{form.duration}</option>}
                </select>
              </div>
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="course-description">Description</Label>
              <Textarea
                id="course-description"
                value={form.description}
                onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
                rows={3}
              />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="course-admission">Admission requirements</Label>
              <Textarea
                id="course-admission"
                value={form.admission_requirements}
                onChange={(e) =>
                  setForm((f) => ({ ...f, admission_requirements: e.target.value }))
                }
                rows={3}
              />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="course-fees">Fee structure</Label>
              <Textarea
                id="course-fees"
                value={form.fee_summary}
                onChange={(e) => setForm((f) => ({ ...f, fee_summary: e.target.value }))}
                rows={3}
                placeholder="Describe the fees; stored as { summary: … }"
              />
            </div>
            {formError && <p className="text-sm text-destructive">{formError}</p>}
            <DialogFooter>
              <Button type="button" variant="outline" onClick={closeModal}>
                Cancel
              </Button>
              <Button type="submit" disabled={saveMutation.isPending}>
                {saveMutation.isPending ? "Saving…" : editing ? "Save changes" : "Create course"}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}
