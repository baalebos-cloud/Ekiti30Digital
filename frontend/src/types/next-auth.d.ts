// Role claims added in src/lib/auth.ts.
import "next-auth";
import "next-auth/jwt";

type Role = "admin" | "contributor";

declare module "next-auth" {
  interface User {
    role: Role;
  }
  interface Session {
    user?: {
      name?: string | null;
      email?: string | null;
      image?: string | null;
      role?: Role;
    };
  }
}

declare module "next-auth/jwt" {
  interface JWT {
    role?: Role;
    /** Backend ContributorAccount.id; contributor tokens only. */
    contributorId?: number;
  }
}
