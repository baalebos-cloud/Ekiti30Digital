"use client";

import { motion } from "motion/react";
import { signOut } from "next-auth/react";
import { useState } from "react";

import { Spinner } from "@/components/ui/Spinner";

/** `variant="nav"` renders it as a nav link instead of a bordered button. */
export function SignOutButton({ variant = "button" }: { variant?: "button" | "nav" }) {
  const [pending, setPending] = useState(false);

  return (
    <motion.button
      type="button"
      disabled={pending}
      whileTap={pending ? undefined : { scale: 0.97 }}
      onClick={() => {
        setPending(true);
        signOut({ callbackUrl: "/login" });
      }}
      className={variant === "nav" ? "nav-link nav-link-button nav-signout" : "btn-secondary btn-flex"}
    >
      {pending && <Spinner size={14} />}
      {pending ? "Signing out…" : "Sign out"}
    </motion.button>
  );
}
