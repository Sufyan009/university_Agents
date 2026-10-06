import { createFileRoute, Link } from "@tanstack/react-router";
import { ArrowRight, GraduationCap, Building2, Sparkles, BookOpen, ShieldCheck, Mic } from "lucide-react";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Scholaria — University Voice AI Platform" },
      { name: "description", content: "Voice AI for universities. Choose your portal to continue." },
    ],
  }),
  component: Landing,
});

function Landing() {
  return (
    <div className="min-h-screen bg-background relative overflow-hidden">
      <div className="pointer-events-none absolute -top-40 -left-40 h-96 w-96 rounded-full bg-primary/20 blur-3xl" />
      <div className="pointer-events-none absolute top-1/2 -right-40 h-96 w-96 rounded-full bg-info/15 blur-3xl" />

      <header className="relative z-10 px-6 lg:px-10 py-5 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="h-9 w-9 rounded-lg bg-gradient-primary flex items-center justify-center shadow-glow">
            <GraduationCap className="h-4.5 w-4.5 text-primary-foreground" />
          </div>
          <span className="font-bold text-lg tracking-tight">Scholaria</span>
        </div>
        <nav className="hidden md:flex items-center gap-8 text-sm text-muted-foreground">
          <a href="#features" className="hover:text-foreground transition-smooth">Features</a>
          <a href="#" className="hover:text-foreground transition-smooth">Pricing</a>
          <a href="#" className="hover:text-foreground transition-smooth">Docs</a>
        </nav>
        <Link to="/app/login" className="text-sm font-medium px-4 py-2 rounded-md hover:bg-muted transition-smooth">
          Sign in
        </Link>
      </header>

      <main className="relative z-10 px-6 lg:px-10 pt-12 lg:pt-20 pb-20">
        <div className="max-w-6xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-border bg-surface text-xs font-medium text-muted-foreground mb-6 shadow-card">
            <Sparkles className="h-3 w-3 text-primary" />
            Voice AI for higher education
          </div>
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight max-w-4xl mx-auto leading-[1.05]">
            Answer every student call,
            <br />
            about admissions, courses, and fees.
          </h1>
          <p className="mt-6 text-base lg:text-lg text-muted-foreground max-w-2xl mx-auto">
            One platform to configure your university's voice agent and answer admissions,
            course, scholarship, and campus questions 24/7 — using only your data.
          </p>

          <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-3">
            <Link
              to="/app/login"
              className="group inline-flex items-center gap-2 px-6 py-3 rounded-lg bg-gradient-primary text-primary-foreground font-semibold shadow-glow hover:shadow-elevated transition-smooth"
            >
              Enter University Portal
              <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
            </Link>
            <Link
              to="/admin/login"
              className="group inline-flex items-center gap-2 px-6 py-3 rounded-lg border border-border bg-surface text-foreground font-semibold hover:bg-muted transition-smooth"
            >
              Enter Super Admin
              <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
            </Link>
          </div>
        </div>

        <div id="features" className="mt-24 lg:mt-32 max-w-6xl mx-auto grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {features.map((f) => (
            <div key={f.title} className="group rounded-2xl border border-border-subtle bg-surface p-6 shadow-card hover:shadow-elevated transition-smooth">
              <div className="h-10 w-10 rounded-lg bg-primary-soft text-primary flex items-center justify-center mb-4">
                <f.icon className="h-5 w-5" />
              </div>
              <h3 className="font-semibold text-foreground">{f.title}</h3>
              <p className="mt-1.5 text-sm text-muted-foreground leading-relaxed">{f.desc}</p>
            </div>
          ))}
        </div>
      </main>

      <footer className="relative z-10 px-6 lg:px-10 py-8 border-t border-border-subtle text-xs text-muted-foreground flex flex-col sm:flex-row items-center justify-between gap-3">
        <span>© 2026 Scholaria. Built for higher education.</span>
        <div className="flex gap-5">
          <a href="#" className="hover:text-foreground">Privacy</a>
          <a href="#" className="hover:text-foreground">Terms</a>
          <a href="#" className="hover:text-foreground">Status</a>
        </div>
      </footer>
    </div>
  );
}

const features = [
  { icon: Mic, title: "AI Voice Answering", desc: "Natural-sounding agents answer student calls 24/7 about admissions, courses, and fees." },
  { icon: Building2, title: "Multi-University", desc: "One platform, many universities. Each has its own phone number, data, and agent." },
  { icon: BookOpen, title: "Course Catalog", desc: "Unlimited courses and subjects, with fees, durations, and entry requirements." },
  { icon: GraduationCap, title: "Admissions & Scholarships", desc: "Eligibility, deadlines, application steps, documents, and scholarship info." },
  { icon: Sparkles, title: "Custom Agent Personality", desc: "Tune the voice, tone, and behaviour to match your institution." },
  { icon: ShieldCheck, title: "Strict Tenant Isolation", desc: "A caller to one university can never reach another's data." },
];
