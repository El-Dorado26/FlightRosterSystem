"use client";

import { useAuth } from "@/contexts/AuthContext";
import { ReactNode } from "react";

interface RoleGuardProps {
  children: ReactNode;
  allowedRoles: string[];
  fallback?: ReactNode;
}

export function RoleGuard({ children, allowedRoles, fallback }: RoleGuardProps) {
  const { user } = useAuth();

  if (!user || !allowedRoles.includes(user.role)) {
    return fallback || null;
  }

  return <>{children}</>;
}

interface FeatureGuardProps {
  children: ReactNode;
  feature: "export" | "save" | "edit" | "delete" | "view";
}

export function FeatureGuard({ children, feature }: FeatureGuardProps) {
  const { user } = useAuth();

  if (!user) return null;

  const permissions: Record<string, string[]> = {
    view: ["admin", "manager", "crew", "viewer"],
    export: ["admin", "manager"],
    save: ["admin", "manager"],
    edit: ["admin", "manager"],
    delete: ["admin"],
  };

  if (!permissions[feature]?.includes(user.role)) {
    return null;
  }

  return <>{children}</>;
}
