// Generate the ADMIN_USERS value for admin login (see src/lib/auth.ts).
//
// Run locally:  node scripts/hash-admin-password.mjs
//
// Prompts for each admin's email and password (the password isn't echoed and
// never touches shell history), bcrypt-hashes it, and prints one line to
// paste into frontend/.env.local:
//
//   ADMIN_USERS=<base64 of [{ email, passwordHash }, ...]>
//
// Base64 because bcrypt hashes contain "$", which Next.js's env loader would
// otherwise try to expand as variables. The output contains hashes, not
// passwords, but still belongs only in .env.local / your host's env settings —
// never in a committed file. Rerun to add or change admins; it always prints
// the complete list.

import readline from "node:readline";

import bcrypt from "bcryptjs";

const BCRYPT_COST = 12;

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
  terminal: Boolean(process.stdin.isTTY),
});

// While muted, typed characters aren't echoed back to the terminal.
let muted = false;
rl._writeToOutput = (text) => {
  if (!muted) rl.output.write(text);
};

// Queue incoming lines so none are lost if input arrives faster than the
// prompts (e.g. pasted or piped input).
const pending = [];
let waiting = null;
let closed = false;
rl.on("line", (line) => {
  if (waiting) {
    const resolve = waiting;
    waiting = null;
    resolve(line);
  } else {
    pending.push(line);
  }
});
rl.on("close", () => {
  closed = true;
  if (waiting) waiting("");
});

function ask(question, { hidden = false } = {}) {
  process.stdout.write(question);
  muted = hidden;
  return new Promise((resolve) => {
    const done = (answer) => {
      muted = false;
      if (hidden) process.stdout.write("\n");
      resolve(answer);
    };
    if (pending.length) done(pending.shift());
    else if (closed) done("");
    else waiting = done;
  });
}

const admins = [];

for (;;) {
  const email = (await ask("Admin email (leave blank to finish): ")).trim().toLowerCase();
  if (!email) break;

  const password = await ask("Password (hidden): ", { hidden: true });
  const confirm = await ask("Confirm password (hidden): ", { hidden: true });
  if (password !== confirm) {
    console.log("Passwords didn't match — try that admin again.\n");
    continue;
  }
  if (password.length < 12) {
    console.log("Use at least 12 characters — try that admin again.\n");
    continue;
  }

  admins.push({ email, passwordHash: await bcrypt.hash(password, BCRYPT_COST) });
  console.log(`Added ${email}.\n`);
}
rl.close();

if (admins.length === 0) {
  console.log("No admins entered; nothing to print.");
  process.exit(1);
}

const value = Buffer.from(JSON.stringify(admins)).toString("base64");
console.log(`\nPaste this line into frontend/.env.local:\n\nADMIN_USERS=${value}\n`);
