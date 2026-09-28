/**
 * Contributor signup rules, shared by the signup form and its API route.
 *
 * Mirrors backend/app/schemas/contributors.py:SignupRequest. The backend
 * stays the source of truth — these only let the form catch mistakes before
 * a round trip, and the route turns the backend's 422s into these messages.
 */

export type SignupField = "name" | "email" | "password";
export type SignupErrors = Partial<Record<SignupField | "confirm", string>>;

export const PASSWORD_MIN = 8;
// bcrypt ignores everything past 72 bytes, so the backend rejects longer.
export const PASSWORD_MAX_BYTES = 72;
export const NAME_MAX = 200;

const EMAIL_RE = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;

export const FIELD_LABELS: Record<SignupField, string> = {
  name: "Name",
  email: "Email",
  password: "Password",
};

export function passwordBytes(password: string): number {
  return new TextEncoder().encode(password).length;
}

export function validateSignup(values: {
  name: string;
  email: string;
  password: string;
  confirm: string;
}): SignupErrors {
  const errors: SignupErrors = {};
  const name = values.name.trim();
  if (!name) errors.name = "Tell us your name.";
  else if (name.length > NAME_MAX) errors.name = `Keep your name under ${NAME_MAX} characters.`;

  if (!values.email.trim()) errors.email = "Enter your email address.";
  else if (!EMAIL_RE.test(values.email.trim())) errors.email = "That doesn't look like an email address.";

  if (values.password.length < PASSWORD_MIN) {
    errors.password = `Use at least ${PASSWORD_MIN} characters.`;
  } else if (passwordBytes(values.password) > PASSWORD_MAX_BYTES) {
    errors.password = "That password is too long — keep it under 72 characters.";
  }

  if (!values.confirm) errors.confirm = "Type your password again to confirm it.";
  else if (values.confirm !== values.password) errors.confirm = "The passwords don't match.";

  return errors;
}
