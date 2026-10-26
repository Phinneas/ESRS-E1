// Tests the role guards against the gitagent runtime's own hook code.
// No model or API key needed: it loads each agent's hooks.yaml with the
// runtime's loader, wraps the runtime's real built-in tools, and calls them.
//
// Usage: node scripts/test_guard.mjs <path to node_modules/@open-gitagent/gitagent>

import { resolve, join } from "node:path";
import { mkdirSync, rmSync, symlinkSync, existsSync, writeFileSync } from "node:fs";
import { spawnSync } from "node:child_process";

const runtime = resolve(process.argv[2] || "node_modules/@open-gitagent/gitagent");
const { loadHooksConfig, runHooks, wrapToolWithHooks } = await import(join(runtime, "dist/hooks.js"));
const { createBuiltinTools } = await import(join(runtime, "dist/tools/index.js"));

const ROOT = resolve(new URL("..", import.meta.url).pathname);
const DIRS = { orchestrator: ROOT, drafter: join(ROOT, "agents/drafter"), reviewer: join(ROOT, "agents/reviewer") };

let pass = 0, fail = 0;
function check(label, got, want) {
  const ok = got === want;
  ok ? pass++ : fail++;
  console.log(`${ok ? "PASS" : "FAIL"}  ${label.padEnd(72)} ${got}${ok ? "" : ` (wanted ${want})`}`);
}

// Decision tests: the exact function the runtime calls before every tool.
async function decide(role, tool, args) {
  const cfg = await loadHooksConfig(DIRS[role]);
  if (!cfg) return "NO HOOKS";
  const prev = process.cwd();
  process.chdir(DIRS[role]); // hooks resolve relative paths from the agent dir, like the tools do
  try { return (await runHooks(cfg.hooks.pre_tool_use, DIRS[role], { event: "pre_tool_use", session_id: "t", tool, args })).action; }
  finally { process.chdir(prev); }
}

// Fixtures
for (const d of ["outputs", "review", "inputs"]) mkdirSync(join(ROOT, d), { recursive: true });
const link = join(ROOT, "review/escape");
rmSync(link, { force: true }); symlinkSync("../outputs", link);

const T = [
  // reviewer
  ["reviewer", "read", { path: "../../knowledge/standards/esrs-datapoints.csv" }, "allow"],
  ["reviewer", "read", { path: "../../outputs/disclosure.md" }, "allow"],
  ["reviewer", "read", { path: "/etc/passwd" }, "block"],
  ["reviewer", "read", { path: "../../.env" }, "block"],
  ["drafter", "read", { path: "../../.env" }, "block"],
  ["orchestrator", "read", { path: ".env" }, "block"],
  ["reviewer", "read", { path: "../../examples/fictional-metalworks/expected-findings.md" }, "block"],
  ["drafter", "read", { path: "../../examples/fictional-metalworks/expected-findings.md" }, "block"],
  ["reviewer", "write", { path: "../../review/findings.md", content: "x" }, "allow"],
  ["reviewer", "write", { path: "../../outputs/disclosure.md", content: "x" }, "block"],
  ["reviewer", "edit", { path: "../../outputs/disclosure.md" }, "block"],
  ["reviewer", "write", { path: "../../review/../outputs/disclosure.md", content: "x" }, "block"],
  ["reviewer", "write", { path: "../../review/escape/disclosure.md", content: "x" }, "block"],
  ["reviewer", "write", { path: join(ROOT, "outputs/disclosure.md"), content: "x" }, "block"],
  ["reviewer", "cli", { command: "echo hi > ../../outputs/disclosure.md" }, "block"],
  ["reviewer", "cli", { command: 'gitagent --dir agents/drafter -p "x"' }, "block"],
  ["reviewer", "memory", { action: "save", content: "x" }, "block"],
  ["reviewer", "skill_learner", {}, "block"],
  ["reviewer", "some_mcp__tool", {}, "block"],
  // drafter
  ["drafter", "write", { path: "../../outputs/disclosure.md", content: "x" }, "allow"],
  ["drafter", "edit", { path: "../../outputs/disclosure.md" }, "allow"],
  ["drafter", "read", { path: "../../review/findings.md" }, "allow"],
  ["drafter", "write", { path: "../../review/findings.md", content: "x" }, "block"],
  ["drafter", "write", { path: "../../approvals/approved.md", content: "x" }, "block"],
  ["drafter", "write", { path: "../../knowledge/standards/esrs-datapoints.csv", content: "x" }, "block"],
  ["drafter", "cli", { command: "git commit -am approve" }, "block"],
  // orchestrator
  ["orchestrator", "cli", { command: 'gitagent --dir agents/drafter -p "Draft E1 from inputs/company.yaml"' }, "allow"],
  ["orchestrator", "cli", { command: 'gitagent --dir agents/reviewer -p "Review outputs/disclosure.md"' }, "allow"],
  ["orchestrator", "cli", { command: 'gitagent --dir agents/reviewer -p "x"; rm -rf review' }, "block"],
  ["orchestrator", "cli", { command: 'gitagent --dir agents/reviewer -p "$(cat /etc/passwd)"' }, "block"],
  ["orchestrator", "cli", { command: 'gitagent --dir agents/reviewer -p "x" && git tag v1' }, "block"],
  ["orchestrator", "cli", { command: 'gitagent --dir ../other -p "x"' }, "block"],
  ["orchestrator", "write", { path: "review/findings.md", content: "x" }, "block"],
  ["orchestrator", "write", { path: "outputs/disclosure.md", content: "x" }, "block"],
  ["orchestrator", "read", { path: "outputs/disclosure.md" }, "allow"],
];

console.log("\n== Hook decisions (runtime runHooks) ==");
for (const [role, tool, args, want] of T)
  check(`${role} ${tool} ${args.path || args.command || ""}`, await decide(role, tool, args), want);

// End-to-end: real runtime tools wrapped with real hooks. Blocked writes must not land.
console.log("\n== Wrapped runtime tools (real file writes) ==");
async function wrapped(role) {
  const cfg = await loadHooksConfig(DIRS[role]);
  return Object.fromEntries(createBuiltinTools({ dir: DIRS[role], timeout: 10 })
    .map((t) => wrapToolWithHooks(t, cfg, DIRS[role], "t")).map((t) => [t.name, t]));
}
async function attempt(role, tool, args) {
  const prev = process.cwd(); process.chdir(DIRS[role]);
  try { await (await wrapped(role))[tool].execute("id", args); return "ran"; }
  catch (e) { return /blocked by hook/.test(e.message) ? "blocked" : `error: ${e.message}`; }
  finally { process.chdir(prev); }
}
const target = join(ROOT, "outputs/e2e-check.md");
rmSync(target, { force: true });
check("reviewer write outputs/e2e-check.md", await attempt("reviewer", "write", { path: "../../outputs/e2e-check.md", content: "tamper" }), "blocked");
check("  ...file absent afterwards", String(existsSync(target)), "false");
check("reviewer cli touch outputs/e2e-check.md", await attempt("reviewer", "cli", { command: "touch ../../outputs/e2e-check.md" }), "blocked");
check("  ...file absent afterwards", String(existsSync(target)), "false");
check("drafter write outputs/e2e-check.md", await attempt("drafter", "write", { path: "../../outputs/e2e-check.md", content: "draft" }), "ran");
check("  ...file present afterwards", String(existsSync(target)), "true");
rmSync(target, { force: true });

// Fail-closed: a broken guard must still block.
console.log("\n== Fail-closed behaviour ==");
function rawHook(dir, stdin, env) {
  const r = spawnSync("/bin/sh", [join(dir, "hooks/guard.sh")], { cwd: dir, input: stdin, env: { ...process.env, ...env } });
  try { return JSON.parse(r.stdout.toString()).action; } catch { return `bad output (exit ${r.status})`; }
}
check("reviewer guard with malformed JSON input", rawHook(DIRS.reviewer, "not json", {}), "block");
check("reviewer guard with node missing from PATH", rawHook(DIRS.reviewer, JSON.stringify({ event: "pre_tool_use", tool: "read", args: { path: "x" } }), { PATH: "/nonexistent" }), "block");
check("unknown event passes through", rawHook(DIRS.reviewer, JSON.stringify({ event: "post_response" }), {}), "allow");

rmSync(link, { force: true });
console.log(`\n${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);
