// Role guard for the gitagent pre_tool_use hook.
//
// The gitagent CLI gives every agent every built-in tool and ignores the
// `tools:` list in agent.yaml. It also lets a tool run if a hook crashes.
// So this guard is the only enforcement point, and it fails closed:
// anything it does not explicitly allow is blocked, and any error blocks.
//
// Usage (from hooks/guard.sh): node guard.mjs <role> <repo_root>
// Reads the hook input JSON on stdin. Prints one JSON line on stdout.

import { readFileSync, realpathSync, existsSync } from "node:fs";
import { resolve, dirname, relative, isAbsolute, sep } from "node:path";
import { homedir } from "node:os";

const [role, rootArg] = process.argv.slice(2);

function out(action, reason, args) {
  const result = { action };
  if (reason) result.reason = reason;
  if (args) result.args = args;
  process.stdout.write(JSON.stringify(result) + "\n");
  process.exit(0);
}
const allow = () => out("allow");
const block = (reason) => out("block", `[${role || "unknown"} guard] ${reason}`);

// Resolve a path the way the gitagent file tools do (relative to the agent's
// own directory, which is also this hook's cwd), then follow symlinks on the
// nearest existing ancestor so ../ and links cannot escape.
function realTarget(p) {
  if (typeof p !== "string" || p === "") return null;
  if (p === "~" || p.startsWith("~/")) p = homedir() + p.slice(1);
  let abs = isAbsolute(p) ? p : resolve(process.cwd(), p);
  let probe = abs;
  const tail = [];
  while (!existsSync(probe)) {
    const parent = dirname(probe);
    if (parent === probe) break;
    tail.unshift(probe.slice(parent.length + 1));
    probe = parent;
  }
  return resolve(realpathSync(probe), ...tail);
}

function inside(target, dir) {
  const rel = relative(dir, target);
  return rel !== "" && rel !== ".." && !rel.startsWith(".." + sep) && !isAbsolute(rel);
}

// Policy. Paths are relative to the repo root.
// read:      where the role may read (empty list = anywhere in the repo)
// deny_read: folders the role may never read (e.g. the example answer keys)
// write:     where write/edit may land
// cli:       regex a shell command must fully match, or null (no shell)
const SAFE_PROMPT = String.raw`"[^"$\x60\\;&|<>(){}\n\r]*"`;
const POLICY = {
  orchestrator: {
    read: [],
    write: [],
    cli: new RegExp(`^gitagent --dir agents/(drafter|reviewer) -p ${SAFE_PROMPT}$`),
  },
  drafter: {
    read: [],
    deny_read: ["examples"],
    write: ["outputs"],
    cli: null,
  },
  reviewer: {
    read: [],
    deny_read: ["examples"],
    write: ["review"],
    cli: null,
  },
};

try {
  const p = POLICY[role];
  if (!p) block(`no policy for role "${role}"`);
  if (!rootArg) block("repo root not given");
  const root = realpathSync(rootArg);

  const input = JSON.parse(readFileSync(0, "utf-8"));
  if (input.event !== "pre_tool_use") allow(); // other events are not tool calls
  const tool = input.tool;
  const args = input.args || {};

  switch (tool) {
    case "read": {
      const t = realTarget(args.path);
      if (!t) block("read without a path");
      if (!(t === root || inside(t, root))) block(`read outside the repo: ${args.path}`);
      if (/(^|[\/])\.env$|\.env$/.test(t)) block(`reading secrets files is not allowed: ${args.path}`);
      if ((p.deny_read || []).some((d) => t === resolve(root, d) || inside(t, resolve(root, d))))
        block(`read not allowed here: ${args.path}`);
      if (p.read.length && !p.read.some((d) => t === resolve(root, d) || inside(t, resolve(root, d))))
        block(`read not allowed here: ${args.path}`);
      allow();
    }
    case "write":
    case "edit": {
      const t = realTarget(args.path);
      if (!t) block(`${tool} without a path`);
      if (!p.write.some((d) => inside(t, resolve(root, d))))
        block(`${tool} not allowed at ${args.path}. This role may only write to: ${p.write.join(", ") || "nothing"}`);
      allow();
    }
    case "cli": {
      if (!p.cli) block("shell commands are not allowed for this role");
      const cmd = typeof args.command === "string" ? args.command.trim() : "";
      if (!p.cli.test(cmd)) block(`shell command not on the allowlist: ${cmd.slice(0, 120)}`);
      // Sub-agent runs are long. Do not let the model pick its own time limit:
      // in the first live run it chose 5 minutes and killed the drafter mid-write.
      const timeout = Number(process.env.ESRS_SUBAGENT_TIMEOUT_SECONDS) || 3600;
      out("modify", undefined, { command: cmd, timeout });
    }
    default:
      // memory, capture_photo, task_tracker, skill_learner, MCP and plugin tools
      block(`tool "${tool}" is not allowed for this role`);
  }
} catch (err) {
  block(`guard error, failing closed: ${err && err.message}`);
}
