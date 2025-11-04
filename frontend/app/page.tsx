"use client";

import { useAuth } from "@/lib/auth-context";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import AuthPage from "@/components/auth/auth-page";

export default function Home() {
  const { isAuthenticated, login } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (isAuthenticated) {
      router.push("/dashboard");
    }
  }, [isAuthenticated, router]);

  const handleLogin = (email: string, role: string) => {
    login(email, role);
    router.push("/dashboard");
  };

  return <AuthPage onLogin={handleLogin} />;
}
