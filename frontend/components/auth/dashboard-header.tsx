"use client";

import { useAuth } from "@/contexts/AuthContext";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { LogOut, User, Shield, Users, Eye } from "lucide-react";

export function DashboardHeader() {
  const { user, logout } = useAuth();

  const getRoleIcon = (role: string) => {
    switch (role) {
      case "admin":
        return <Shield className="h-4 w-4" />;
      case "manager":
        return <Users className="h-4 w-4" />;
      case "crew":
        return <User className="h-4 w-4" />;
      default:
        return <Eye className="h-4 w-4" />;
    }
  };

  const getRoleBadgeVariant = (role: string) => {
    switch (role) {
      case "admin":
        return "default";
      case "manager":
        return "secondary";
      case "crew":
        return "outline";
      default:
        return "outline";
    }
  };

  return (
    <div className="bg-white border-b sticky top-0 z-50 shadow-sm">
      <div className="container mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="bg-blue-600 text-white p-2 rounded-lg">
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">OpenAIrlines</h1>
              <p className="text-xs text-gray-500">Flight Roster Management System</p>
            </div>
          </div>

          {user && (
            <div className="flex items-center gap-4">
              <Card className="border-gray-200">
                <CardContent className="p-3">
                  <div className="flex items-center gap-3">
                    <div className="bg-blue-100 p-2 rounded-full">
                      <User className="h-4 w-4 text-blue-600" />
                    </div>
                    <div className="text-left">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-semibold text-gray-900">{user.name || user.email}</span>
                        <Badge variant={getRoleBadgeVariant(user.role)} className="flex items-center gap-1">
                          {getRoleIcon(user.role)}
                          {user.role}
                        </Badge>
                      </div>
                      <span className="text-xs text-gray-500">{user.email}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Button onClick={logout} variant="outline" size="sm" className="flex items-center gap-2">
                <LogOut className="h-4 w-4" />
                Logout
              </Button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
