"use client";

import { AnimatePresence, motion, useAnimationControls } from "motion/react";
import Link from "next/link";
import { useState } from "react";

import { FieldError } from "@/components/ui/FieldError";
import { Spinner } from "@/components/ui/Spinner";
import { SuccessCheck } from "@/components/ui/SuccessCheck";
import { PASSWORD_MIN, validateSignup, type SignupErrors } from "@/lib/signup";

type Status = "idle" | "submitting" | "success";
type Values = { name: string; email: string; password: string; confirm: string };
type Feedback = { message: string; signInLink?: boolean };

const EMPTY: Values = { name: "", email: "", password: "", confirm: "" };
const FIELD_ORDER = ["name", "email", "password", "confirm"] as const;

export function SignupForm() {
  const card = useAnimationControls();
  const [values, setValues] = useState<Values>(EMPTY);
  const [errors, setErrors] = useState<SignupErrors>({});
  const [feedback, setFeedback] = useState<Feedback | null>(null);
  const [status, setStatus] = useState<Status>("idle");
  const [showPassword, setShowPassword] = useState(false);
  const busy = status !== "idle";

  function setValue(name: keyof Values, value: string) {
    setValues((v) => ({ ...v, [name]: value }));
    if (errors[name]) setErrors((e) => ({ ...e, [name]: undefined }));
  }

  function fail(next: SignupErrors, message: Feedback) {
    setErrors(next);
    setFeedback(message);
    card.start({ x: [0, -10, 9, -6, 4, 0], transition: { duration: 0.45 } });
    const first = FIELD_ORDER.find((f) => next[f]);
    if (first) document.getElementById(first)?.focus();
  }

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (busy) return;
    setFeedback(null);

    const found = validateSignup(values);
    if (Object.keys(found).length > 0) {
      fail(found, { message: "A few details need your attention." });
      return;
    }

    setStatus("submitting");
    let response: Response;
    try {
      response = await fetch("/api/signup", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: values.name.trim(), email: values.email.trim(), password: values.password }),
      });
    } catch {
      setStatus("idle");
      fail({}, { message: "Couldn't reach the server. Check your connection and try again." });
      return;
    }
    const data = (await response.json().catch(() => null)) as { errors?: SignupErrors } | null;

    if (response.status === 201) {
      setStatus("success");
      return;
    }
    setStatus("idle");
    if (response.status === 409) {
      fail(
        { email: "This email is already registered." },
        { message: "An account with this email already exists.", signInLink: true },
      );
    } else if (response.status === 422 && data?.errors && Object.keys(data.errors).length > 0) {
      fail(data.errors, { message: "Some details weren't accepted — see the highlighted fields." });
    } else {
      fail({}, { message: "Sign-up isn't available right now. Please try again in a moment." });
    }
  }

  const passwordLongEnough = values.password.length >= PASSWORD_MIN;
  const passwordsMatch = values.confirm.length > 0 && values.confirm === values.password;
  const firstName = values.name.trim().split(/\s+/)[0];

  return (
    <motion.div
      initial={{ opacity: 0, y: 24 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
      className="w-full max-w-md"
    >
      <motion.div animate={card} className="form-card overflow-hidden">
        <div className="form-card-band" />
        <div className="px-7 pb-8 pt-7 sm:px-9">
          <AnimatePresence mode="wait" initial={false}>
            {status === "success" ? (
              <motion.div
                key="success"
                initial={{ opacity: 0, scale: 0.96 }}
                animate={{ opacity: 1, scale: 1 }}
                className="flex flex-col items-center py-6 text-center"
                role="status"
              >
                <SuccessCheck />
                <motion.div
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.35, duration: 0.4 }}
                  className="flex flex-col items-center"
                >
                  <p className="mt-5 font-display text-2xl text-forest">
                    Ẹ ṣeun{firstName ? `, ${firstName}` : ""} — almost there.
                  </p>
                  <span className="status-pill mt-3">Awaiting approval</span>
                  <p className="mt-4 text-sm text-ink-soft">
                    Your account has been created, but it isn&apos;t active yet. An admin from the
                    EKITI@30 team will review it — once it&apos;s approved, you can sign in with{" "}
                    <strong className="font-semibold text-ink">{values.email.trim()}</strong>.
                  </p>
                  <Link href="/login" className="btn-secondary mt-6">
                    Go to sign in
                  </Link>
                </motion.div>
              </motion.div>
            ) : (
              <motion.div key="form" exit={{ opacity: 0, scale: 0.98 }}>
                <div className="eyebrow-row mb-3">
                  <span className="eyebrow-dot" /> Darapọ̀ mọ́ wa · Join us
                </div>
                <h1 className="font-display text-3xl font-medium tracking-tight">
                  Join the <em className="text-forest-2">archive</em>
                </h1>
                <p className="mt-2 text-sm text-ink-soft">
                  Create a contributor account to share photos and videos of Ekiti&apos;s thirty
                  years. The EKITI@30 team approves new accounts before they can sign in.
                </p>

                <form onSubmit={handleSubmit} className="mt-7 flex flex-col gap-5" noValidate>
                  <div className="field">
                    <label htmlFor="name" className="field-label">Your name</label>
                    <input
                      id="name"
                      value={values.name}
                      onChange={(e) => setValue("name", e.target.value)}
                      autoComplete="name"
                      disabled={busy}
                      aria-invalid={errors.name ? true : undefined}
                      aria-describedby="name-error"
                      className="input"
                      placeholder="How you'd like to be credited"
                    />
                    <FieldError id="name-error" message={errors.name} />
                  </div>

                  <div className="field">
                    <label htmlFor="email" className="field-label">Email</label>
                    <input
                      id="email"
                      type="email"
                      value={values.email}
                      onChange={(e) => setValue("email", e.target.value)}
                      autoComplete="email"
                      disabled={busy}
                      aria-invalid={errors.email ? true : undefined}
                      aria-describedby="email-error"
                      className="input"
                      placeholder="you@example.com"
                    />
                    <FieldError id="email-error" message={errors.email} />
                  </div>

                  <div className="field">
                    <label htmlFor="password" className="field-label">Password</label>
                    <div className="relative">
                      <input
                        id="password"
                        type={showPassword ? "text" : "password"}
                        value={values.password}
                        onChange={(e) => setValue("password", e.target.value)}
                        autoComplete="new-password"
                        disabled={busy}
                        aria-invalid={errors.password ? true : undefined}
                        aria-describedby="password-rule password-error"
                        className="input pr-16"
                      />
                      <button
                        type="button"
                        onClick={() => setShowPassword((v) => !v)}
                        className="absolute inset-y-0 right-2 my-auto h-8 rounded px-2 text-xs font-semibold text-ink-soft hover:text-forest"
                        aria-pressed={showPassword}
                      >
                        {showPassword ? "Hide" : "Show"}
                      </button>
                    </div>
                    <Requirement id="password-rule" met={passwordLongEnough}>
                      At least {PASSWORD_MIN} characters
                    </Requirement>
                    <FieldError id="password-error" message={errors.password} />
                  </div>

                  <div className="field">
                    <label htmlFor="confirm" className="field-label">Confirm password</label>
                    <input
                      id="confirm"
                      type={showPassword ? "text" : "password"}
                      value={values.confirm}
                      onChange={(e) => setValue("confirm", e.target.value)}
                      autoComplete="new-password"
                      disabled={busy}
                      aria-invalid={errors.confirm ? true : undefined}
                      aria-describedby="confirm-rule confirm-error"
                      className="input"
                    />
                    <Requirement id="confirm-rule" met={passwordsMatch}>
                      Passwords match
                    </Requirement>
                    <FieldError id="confirm-error" message={errors.confirm} />
                  </div>

                  <AnimatePresence>
                    {feedback && (
                      <motion.div
                        key="feedback"
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: "auto" }}
                        exit={{ opacity: 0, height: 0 }}
                        className="overflow-hidden"
                      >
                        <div className="alert alert-error" role="alert">
                          <span aria-hidden="true">●</span>
                          <span>
                            {feedback.message}
                            {feedback.signInLink && (
                              <>
                                {" "}
                                <Link href="/login" className="font-semibold underline underline-offset-2">
                                  Sign in instead
                                </Link>
                              </>
                            )}
                          </span>
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>

                  <motion.button
                    type="submit"
                    disabled={busy}
                    whileHover={busy ? undefined : { y: -1 }}
                    whileTap={busy ? undefined : { scale: 0.97 }}
                    className="btn-primary btn-flex mt-1"
                  >
                    {status === "submitting" ? (
                      <>
                        <Spinner /> Creating your account…
                      </>
                    ) : (
                      "Create account"
                    )}
                  </motion.button>
                </form>

                <p className="mt-6 border-t border-dashed border-line pt-5 text-center text-sm text-ink-soft">
                  Already have an account?{" "}
                  <Link href="/login" className="link-btn">
                    Sign in
                  </Link>
                </p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </motion.div>
    </motion.div>
  );
}

/** A live requirement hint: grey until met, then forest with a drawn check. */
function Requirement({ id, met, children }: { id: string; met: boolean; children: React.ReactNode }) {
  return (
    <p id={id} className={`requirement ${met ? "is-met" : ""}`}>
      <span className="requirement-dot" aria-hidden="true">
        <AnimatePresence initial={false}>
          {met && (
            <motion.svg
              key="check"
              viewBox="0 0 24 24"
              width="10"
              height="10"
              fill="none"
              initial={{ scale: 0.4, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.4, opacity: 0 }}
              transition={{ type: "spring", stiffness: 420, damping: 20 }}
            >
              <motion.path
                d="M5 12.5l4.5 4.5L19 7.5"
                stroke="var(--gold-soft)"
                strokeWidth="3.6"
                strokeLinecap="round"
                strokeLinejoin="round"
                initial={{ pathLength: 0 }}
                animate={{ pathLength: 1 }}
                transition={{ duration: 0.25, ease: "easeOut" }}
              />
            </motion.svg>
          )}
        </AnimatePresence>
      </span>
      {children}
      <span className="sr-only">{met ? " — done" : " — not yet"}</span>
    </p>
  );
}
