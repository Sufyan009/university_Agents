import { createFileRoute, useNavigate, Link } from "@tanstack/react-router";
import { useState } from "react";
import { GraduationCap, Building2 } from "lucide-react";
import { universityLogin, saveToken, saveRole, savePermissions } from "@/lib/api/auth";

export const Route = createFileRoute("/app/login")({
  component: UniversityLogin,
});

function UniversityLogin() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const res = await universityLogin({ email, password });
      saveToken(res.access_token);
      saveRole(res.role);
      savePermissions(res.permissions);
      navigate({ to: "/app/dashboard" });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-background flex items-center justify-center px-4">
      <div className="w-full max-w-sm">
        <div className="flex items-center justify-center gap-2.5 mb-8">
          <div className="h-9 w-9 rounded-lg bg-gradient-primary flex items-center justify-center shadow-glow">
            <GraduationCap className="h-4.5 w-4.5 text-primary-foreground" />
          </div>
          <span className="font-bold text-lg tracking-tight">Scholaria</span>
        </div>

        <div className="rounded-2xl border border-border bg-surface p-8 shadow-card">
          <div className="flex items-center gap-2 mb-1">
            <Building2 className="h-5 w-5 text-primary" />
            <h1 className="text-xl font-semibold">University Portal</h1>
          </div>
          <p className="text-sm text-muted-foreground mb-6">Sign in to manage your university</p>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1.5" htmlFor="email">Email</label>
              <input
                id="email"
                type="email"
                required
                autoComplete="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-smooth"
                placeholder="you@university.edu"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1.5" htmlFor="password">Password</label>
              <input
                id="password"
                type="password"
                required
                autoComplete="current-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-smooth"
                placeholder="••••••••"
              />
            </div>

            {error && (
              <p className="text-sm text-destructive bg-destructive/10 rounded-md px-3 py-2">{error}</p>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-lg bg-gradient-primary text-primary-foreground font-semibold py-2.5 text-sm shadow-glow hover:shadow-elevated transition-smooth disabled:opacity-60"
            >
              {loading ? "Signing in…" : "Sign in"}
            </button>
          </form>
        </div>

        <p className="mt-6 text-center text-xs text-muted-foreground">
          Platform admin?{" "}
          <Link to="/admin/login" className="text-primary hover:underline">Admin portal →</Link>
        </p>
      </div>
    </div>
  );
}
