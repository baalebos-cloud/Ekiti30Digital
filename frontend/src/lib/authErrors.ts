/**
 * Error codes authorize() (src/lib/auth.ts) throws when sign-in fails for a
 * reason other than wrong credentials. NextAuth passes a thrown error's
 * message to signIn() as `result.error`, so LoginForm can show a specific
 * message. Wrong credentials instead return null, which surfaces as the
 * generic "CredentialsSignin" — never distinguished between admin and
 * contributor, or between unknown email and wrong password.
 *
 * Kept separate from auth.ts so client components can import it.
 */
export const AUTH_ERRORS = {
  /** Right password, contributor account still awaiting admin review. */
  pending: "AccountPending",
  /** Right password, contributor account rejected. */
  rejected: "AccountNotApproved",
  /** The backend couldn't be reached or answered unexpectedly. */
  unavailable: "LoginUnavailable",
} as const;
