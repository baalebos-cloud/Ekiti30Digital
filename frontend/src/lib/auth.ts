/**
 * NextAuth configuration for admin login.
 *
 * - Credentials provider backed by ADMIN_USERS (base64-encoded JSON list of
 *   { email, passwordHash } bcrypt entries). Generate it with
 *   `node scripts/hash-admin-password.mjs` — plaintext passwords never live
 *   in code or env files.
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

type AdminUser = { email: string; passwordHash: string };

// Admin sessions expire after 8 hours.
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

function signingKey(secret: string | Buffer): Uint8Array {
  return typeof secret === "string" ? new TextEncoder().encode(secret) : new Uint8Array(secret);
}

export const authOptions: NextAuthOptions = {
  session: { strategy: "jwt", maxAge: SESSION_MAX_AGE },
  providers: [
    CredentialsProvider({
      name: "Admin login",
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
        if (!admin || !valid) return null;

        return { id: admin.email, email: admin.email };
      },
    }),
  ],
  callbacks: {
    async jwt({ token, user }) {
      // Only admins can log in, so every issued token carries role=admin,
      // which the backend's require_admin checks for.
      if (user?.email) {
        token.sub = user.email;
        token.email = user.email;
        token.role = "admin";
      }
      return token;
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
