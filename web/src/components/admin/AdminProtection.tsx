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
    if (!userState.isInitial && !userState.isLoading && (!user || !user.isAdmin)) {
      console.log("isInit", userState.isInitial);
      console.log("user", user);
      router.push("/");
    }
  }, [user, userState.isInitial, router]);

  if (userState.isInitial || userState.isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading...</p>
        </div>
      </div>
    );
  }

  if (!user?.isAdmin) {
    return null;
  }

  return <>{children}</>;
}
