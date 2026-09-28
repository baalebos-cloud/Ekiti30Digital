/**
 * NextAuth configuration for admin and contributor login.
 *
 * - One credentials provider, two account sources, checked in order:
 *   1. ADMIN_USERS (base64-encoded JSON list of { email, passwordHash }
 *      bcrypt entries). Generate it with `node scripts/hash-admin-password.mjs`
 *      — plaintext passwords never live in code or env files. → role "admin"
 *   2. The backend's contributor accounts, via POST /api/auth/login.
 *      → role "contributor"
 * - Sessions are JWTs signed with HS256 using NEXTAUTH_SECRET (instead of
 *   NextAuth's default encrypted JWE), so the FastAPI backend can verify them
 *   with the same shared secret (see backend/app/core/auth.py).
 */

import bcrypt from "bcryptjs";
import { jwtVerify, SignJWT } from "jose";
import type { NextAuthOptions } from "next-auth";
import type { JWT } from "next-auth/jwt";
import CredentialsProvider from "next-auth/providers/credentials";
import { cookies } from "next/headers";

import { AUTH_ERRORS } from "@/lib/authErrors";
import { API_URL } from "@/lib/config";

type AdminUser = { email: string; passwordHash: string };

// Sessions (admin and contributor) expire after 8 hours.
const SESSION_MAX_AGE = 8 * 60 * 60;

// bcrypt hash of a random string nobody knows. Compared against when the
// email doesn't match an admin, so a login attempt takes the same time
// whether or not the email exists.
const DUMMY_HASH = "$2b$12$3PmYf9cGM0TSuY4tAwHDnORFuSDjrtOCxiEx3oS5kp1z.1LFrRonG";

function loadAdmins(): AdminUser[] {
  const raw = process.env.ADMIN_USERS;
  if (!raw) return [];
  try {
    const parsed: unknown = JSON.parse(Buffer.from(raw, "base64").toString("utf8"));
    if (
      Array.isArray(parsed) &&
      parsed.every(
        (a) => typeof a?.email === "string" && typeof a?.passwordHash === "string",
      )
    ) {
      return parsed as AdminUser[];
    }
  } catch {
    // fall through
  }
  console.error("ADMIN_USERS is set but invalid — regenerate it with scripts/hash-admin-password.mjs");
  return [];
}

/**
 * Check credentials against the backend's contributor accounts.
 *
 * Returns the account on success and null for wrong credentials (401).
 * Throws an AUTH_ERRORS code when the password was right but the account
 * isn't approved (403), or when the backend can't answer.
 */
async function loginContributor(email: string, password: string) {
  let response: Response;
  try {
    response = await fetch(`${API_URL}/api/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
      cache: "no-store",
      signal: AbortSignal.timeout(10_000),
    });
  } catch {
    throw new Error(AUTH_ERRORS.unavailable);
  }

  if (response.status === 401) return null;
  if (response.status === 403) {
    // The backend's `code` says which kind of unapproved account this is.
    // Anything else means the contract changed, so claim neither.
    const code = ((await response.json().catch(() => null)) as { code?: unknown } | null)?.code;
    if (code === "pending") throw new Error(AUTH_ERRORS.pending);
    if (code === "rejected") throw new Error(AUTH_ERRORS.rejected);
    throw new Error(AUTH_ERRORS.unavailable);
  }
  if (!response.ok) throw new Error(AUTH_ERRORS.unavailable);

  const account = (await response.json().catch(() => null)) as
    | { id?: unknown; name?: unknown; email?: unknown }
    | null;
  if (typeof account?.id !== "number" || typeof account.email !== "string") {
    throw new Error(AUTH_ERRORS.unavailable);
  }
  return {
    id: String(account.id),
    email: account.email,
    name: typeof account.name === "string" ? account.name : null,
  };
}

function signingKey(secret: string | Buffer): Uint8Array {
  return typeof secret === "string" ? new TextEncoder().encode(secret) : new Uint8Array(secret);
}

export const authOptions: NextAuthOptions = {
  session: { strategy: "jwt", maxAge: SESSION_MAX_AGE },
  providers: [
    CredentialsProvider({
      name: "Email and password",
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" },
      },
      async authorize(credentials) {
        const email = credentials?.email?.trim().toLowerCase();
        const password = credentials?.password;
        if (!email || !password) return null;

        const admin = loadAdmins().find((a) => a.email.toLowerCase() === email);
        const valid = await bcrypt.compare(password, admin?.passwordHash ?? DUMMY_HASH);
        if (admin && valid) return { id: admin.email, email: admin.email, role: "admin" };

        // Not an admin (or not the admin's password): try contributor accounts.
        const contributor = await loginContributor(email, password);
        return contributor ? { ...contributor, role: "contributor" } : null;
      },
    }),
  ],
  callbacks: {
    async jwt({ token, user }) {
      // `user` is only set at sign-in. The claims here are what the backend's
      // require_admin / require_contributor read: sub, email, role (+ exp,
      // added in encode below).
      if (user?.email) {
        token.sub = user.email;
        token.email = user.email;
        token.name = user.name ?? null;
        token.role = user.role;
        if (user.role === "contributor") token.contributorId = Number(user.id);
      }
      return token;
    },
    async session({ session, token }) {
      if (session.user) session.user.role = token.role;
      return session;
    },
  },
  jwt: {
    // Must be set here too: with a custom encode/decode, NextAuth otherwise
    // passes its 30-day default to encode() instead of session.maxAge.
    maxAge: SESSION_MAX_AGE,
    async encode({ token, secret, maxAge }) {
      return new SignJWT({ ...token })
        .setProtectedHeader({ alg: "HS256" })
        .setIssuedAt()
        .setExpirationTime(Math.floor(Date.now() / 1000) + (maxAge ?? SESSION_MAX_AGE))
        .sign(signingKey(secret));
    },
    async decode({ token, secret }) {
      if (!token) return null;
      try {
        const { payload } = await jwtVerify(token, signingKey(secret), {
          algorithms: ["HS256"],
        });
        return payload as JWT;
      } catch {
        return null;
      }
    },
  },
};

/**
 * Server-side only: the Authorization header for calling protected backend
 * routes (e.g. /api/admin/*) as the logged-in admin. The session cookie is
 * httpOnly, so this must run in a server component, route handler, or
 * server action — never in the browser.
 */
export async function getBackendAuthHeader(): Promise<Record<string, string>> {
  const store = await cookies();
  const token =
    store.get("__Secure-next-auth.session-token")?.value ??
    store.get("next-auth.session-token")?.value;
  return token ? { Authorization: `Bearer ${token}` } : {};
}
