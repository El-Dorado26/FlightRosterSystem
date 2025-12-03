"use client";

import { useAuth } from "@/contexts/AuthContext";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import AuthPage from "@/components/auth/auth-page";

export default function Home() {
  const { isAuthenticated } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (isAuthenticated) {
      router.push("/dashboard");
    }
  }, [isAuthenticated, router]);

  const handleLogin = () => {
    // Login is already handled by auth-page.tsx using authService
    // Just redirect to dashboard after successful login
    router.push("/dashboard");
  };

  return <AuthPage onLogin={handleLogin} />;
}
