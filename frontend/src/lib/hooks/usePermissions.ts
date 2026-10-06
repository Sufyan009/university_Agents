import { getPermissions } from "@/lib/api/auth";

const PERMISSION_MAP = {
  view_dashboard: "view_dashboard",
  manage_courses: "manage_courses",
  manage_admissions: "manage_admissions",
  configure_voice_agent: "configure_voice_agent",
  manage_users: "manage_users",
  manage_knowledge: "manage_knowledge",
} as const;

export function usePermissions() {
  const permissions = getPermissions();

  const hasPermission = (permission: string): boolean => permissions.includes(permission);

  return {
    hasPermission,
    canViewDashboard: () => hasPermission(PERMISSION_MAP.view_dashboard),
    canManageCourses: () => hasPermission(PERMISSION_MAP.manage_courses),
    canManageAdmissions: () => hasPermission(PERMISSION_MAP.manage_admissions),
    canConfigureVoiceAgent: () => hasPermission(PERMISSION_MAP.configure_voice_agent),
    canManageUsers: () => hasPermission(PERMISSION_MAP.manage_users),
    canManageKnowledge: () => hasPermission(PERMISSION_MAP.manage_knowledge),
    permissions,
  };
}
