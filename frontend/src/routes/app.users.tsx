import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { Mail, Plus, Trash2, X } from "lucide-react";

import { PageHeader } from "@/components/shared/PageHeader";
import { StatusPill } from "@/components/shared/StatusPill";
import {
  listUsers,
  inviteUser,
  updateUserRole,
  removeUser,
  type UniversityUser,
} from "@/lib/api/roles";
import { usePermissions } from "@/lib/hooks/usePermissions";

export const Route = createFileRoute("/app/users")({
  head: () => ({
    meta: [
      { title: "Users & Roles — Scholaria" },
      { name: "description", content: "Invite team members and manage roles." },
    ],
  }),
  component: UsersPage,
});

const ROLES = ["owner", "manager", "operator"] as const;
type AssignableRole = (typeof ROLES)[number];

function UsersPage() {
  const { canManageUsers } = usePermissions();
  const canEdit = canManageUsers();

  const [users, setUsers] = useState<UniversityUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [showInvite, setShowInvite] = useState(false);
  const [inviteEmail, setInviteEmail] = useState("");
  const [inviteRole, setInviteRole] = useState<AssignableRole>("manager");
  const [inviting, setInviting] = useState(false);
  const [inviteError, setInviteError] = useState<string | null>(null);

  const loadUsers = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await listUsers();
      setUsers(res.items);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load users");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadUsers();
  }, []);

  const handleInvite = async () => {
    if (!inviteEmail.trim()) {
      setInviteError("Email is required.");
      return;
    }
    try {
      setInviting(true);
      setInviteError(null);
      await inviteUser({ email: inviteEmail.trim(), role: inviteRole });
      setInviteEmail("");
      setInviteRole("manager");
      setShowInvite(false);
      await loadUsers();
    } catch (err) {
      setInviteError(err instanceof Error ? err.message : "Failed to invite user");
    } finally {
      setInviting(false);
    }
  };

  const handleRoleChange = async (userId: string, role: AssignableRole) => {
    const prev = users;
    setUsers((list) => list.map((u) => (u.id === userId ? { ...u, role } : u)));
    try {
      await updateUserRole(userId, role);
    } catch (err) {
      setUsers(prev);
      alert(err instanceof Error ? err.message : "Failed to update role");
    }
  };

  const handleRemove = async (userId: string) => {
    if (!confirm("Remove this user?")) return;
    try {
      await removeUser(userId);
      setUsers((list) => list.filter((u) => u.id !== userId));
    } catch (err) {
      alert(err instanceof Error ? err.message : "Failed to remove user");
    }
  };

  return (
    <div className="mx-auto max-w-[1200px] px-4 py-6 lg:px-8 lg:py-8">
      <PageHeader
        title="Users & Roles"
        description="Manage who can access this university and what they can do."
        actions={
          canEdit ? (
            <button
              onClick={() => {
                setInviteError(null);
                setShowInvite(true);
              }}
              className="inline-flex h-9 items-center gap-2 rounded-md bg-gradient-primary px-3.5 text-sm font-semibold text-primary-foreground shadow-card transition-smooth hover:shadow-elevated"
            >
              <Plus className="h-4 w-4" />
              Invite user
            </button>
          ) : undefined
        }
      />

      {error && (
        <div className="mb-4 rounded-lg bg-destructive/10 p-3 text-sm text-destructive">{error}</div>
      )}

      {!canEdit && (
        <div className="mb-4 rounded-lg bg-muted p-3 text-sm text-muted-foreground">
          You have view-only access. Contact an owner to manage users.
        </div>
      )}

      {showInvite && canEdit && (
        <div className="mb-6 rounded-xl border border-border-subtle bg-surface p-5 shadow-card">
          <div className="mb-4 flex items-center justify-between">
            <h3 className="font-semibold">Invite a user</h3>
            <button
              onClick={() => setShowInvite(false)}
              className="rounded-md p-1 text-muted-foreground hover:bg-muted"
              aria-label="Close"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
          {inviteError && (
            <div className="mb-3 rounded-lg bg-destructive/10 p-2.5 text-sm text-destructive">
              {inviteError}
            </div>
          )}
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <div className="space-y-1.5 sm:col-span-2">
              <label className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                Email
              </label>
              <input
                type="email"
                className="input"
                value={inviteEmail}
                onChange={(e) => setInviteEmail(e.target.value)}
                placeholder="person@example.com"
              />
            </div>
            <div className="space-y-1.5">
              <label className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                Role
              </label>
              <select
                className="select"
                value={inviteRole}
                onChange={(e) => setInviteRole(e.target.value as AssignableRole)}
              >
                {ROLES.map((r) => (
                  <option key={r} value={r}>
                    {r.charAt(0).toUpperCase() + r.slice(1)}
                  </option>
                ))}
              </select>
            </div>
          </div>
          <button
            onClick={handleInvite}
            disabled={inviting}
            className="mt-4 h-9 rounded-md bg-primary px-4 text-sm font-medium text-primary-foreground transition-smooth hover:bg-primary/90 disabled:opacity-60"
          >
            {inviting ? "Inviting..." : "Send invite"}
          </button>
        </div>
      )}

      <div className="overflow-hidden rounded-xl border border-border-subtle bg-surface shadow-card">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="border-b border-border-subtle bg-surface-elevated">
              <tr className="text-left text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                <th className="px-4 py-3">Name</th>
                <th className="px-4 py-3 hidden sm:table-cell">Role</th>
                <th className="px-4 py-3 hidden md:table-cell">Status</th>
                <th className="px-4 py-3 text-right" />
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan={4} className="px-4 py-12 text-center text-muted-foreground">
                    Loading users...
                  </td>
                </tr>
              ) : users.length === 0 ? (
                <tr>
                  <td colSpan={4} className="px-4 py-12 text-center text-muted-foreground">
                    No users yet. Invite someone to get started.
                  </td>
                </tr>
              ) : (
                users.map((u) => (
                  <tr
                    key={u.id}
                    className="border-b border-border-subtle transition-smooth last:border-0 hover:bg-muted/40"
                  >
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-3">
                        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-gradient-primary text-xs font-semibold text-primary-foreground">
                          {(u.full_name || u.email)
                            .split(" ")
                            .map((p) => p[0])
                            .join("")
                            .slice(0, 2)
                            .toUpperCase()}
                        </div>
                        <div className="min-w-0">
                          <div className="truncate font-medium">{u.full_name || "—"}</div>
                          <div className="flex items-center gap-1 truncate text-xs text-muted-foreground">
                            <Mail className="h-3 w-3 shrink-0" />
                            <span className="truncate">{u.email}</span>
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-3 hidden sm:table-cell">
                      {canEdit && u.role !== "admin" ? (
                        <select
                          className="select w-auto"
                          value={u.role}
                          onChange={(e) =>
                            handleRoleChange(u.id, e.target.value as AssignableRole)
                          }
                        >
                          {ROLES.map((r) => (
                            <option key={r} value={r}>
                              {r.charAt(0).toUpperCase() + r.slice(1)}
                            </option>
                          ))}
                        </select>
                      ) : (
                        <StatusPill
                          label={u.role.charAt(0).toUpperCase() + u.role.slice(1)}
                          tone="info"
                          dot={false}
                        />
                      )}
                    </td>
                    <td className="px-4 py-3 hidden md:table-cell">
                      <StatusPill
                        label={u.is_active ? "Active" : "Inactive"}
                        tone={u.is_active ? "success" : "neutral"}
                      />
                    </td>
                    <td className="px-4 py-3 text-right">
                      {canEdit && (
                        <button
                          onClick={() => handleRemove(u.id)}
                          className="rounded-md p-1.5 text-destructive transition-smooth hover:bg-destructive/10"
                          aria-label="Remove user"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      <style>{`
        .input, .select {
          width: 100%;
          padding: 0.5rem 0.75rem;
          border-radius: 0.375rem;
          border: 1px solid var(--color-border);
          background: var(--color-background);
          font-size: 0.875rem;
        }
        .input:focus, .select:focus {
          outline: none;
          box-shadow: 0 0 0 2px var(--color-ring);
          border-color: transparent;
        }
      `}</style>
    </div>
  );
}
