"use client";

import { useAppSelector } from "@/lib/store";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

interface AdminProtectionProps {
  children: React.ReactNode;
}

export function AdminProtection({ children }: AdminProtectionProps) {
  const user = useAppSelector((state) => state.user.user);
  const userState = useAppSelector((state) => state.user);
  const router = useRouter();

  useEffect(() => {
    console.log("AdminProtection - user:", user);
    console.log("AdminProtection - user.isAdmin:", user?.isAdmin);
    console.log("AdminProtection - userState.isInitial:", userState.isInitial);

    // Only redirect if user is loaded and not admin
    // Don't redirect if still initializing
    if (!userState.isInitial && (!user || !user.isAdmin)) {
      console.log(
        "AdminProtection - redirecting because:",
        !user ? "no user" : "not admin"
      );
      router.push("/");
    }
  }, [user, userState.isInitial, router]);

  // Show loading or redirect if user is not admin
  if (!user) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading...</p>
        </div>
      </div>
    );
  }

  // If user is not admin, don't render children (will redirect)
  if (!user.isAdmin) {
    return null;
  }

  // If user is admin, render children
  return <>{children}</>;
}
