// self-improving-loop — DSH cordis plugin.
// Registers the bundled "self-improve" skill into the DSH skill registry so it
// appears in the session skill catalog and is loadable via the `skill` tool.
// The same skills/self-improve/SKILL.md is shared by every platform adapter
// (Claude Code / Codex / Cursor / Hermes) — one source of truth.
// Tests: test/dsh.test.mjs (mock ctx).
import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { dirname, join } from 'node:path'

export const name = 'self-improving-loop'
export const inject = ['skills']

const here = dirname(fileURLToPath(import.meta.url))
const SKILL_MD = join(here, '..', 'skills', 'self-improve', 'SKILL.md')
const SOURCE = 'https://github.com/DYNO-SOFT/self-improving-loop'

function parseFrontmatter(md) {
  const m = /^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$/.exec(md)
  if (!m) {
    return {
      name: 'self-improve',
      description: 'Self-improvement loop and cognitive-error guardrails.',
      body: md.trim(),
    }
  }
  const fm = m[1]
  const body = m[2].trim()
  const name = (/^name:\s*(.+)$/m.exec(fm) || [])[1]?.trim() || 'self-improve'
  const description =
    (/^description:\s*(.+)$/m.exec(fm) || [])[1]?.trim() ||
    'Self-improvement loop and cognitive-error guardrails.'
  return { name, description, body }
}

// DSH counterpart of the Claude Code / Codex SessionStart hook: a short, cache-safe
// runtime context that keeps the loop active without inlining the whole skill.
export const REMINDER =
  'Self-improvement is active this session. Load the self-improve skill to read shared ' +
  'and applicable project lessons. Before claiming work is done, fixed, or verified, ' +
  'audit for cognitive errors (executed? ' +
  'exit code checked? numbers, not guesses?) and save durable lessons (' +
  'facts -> the shared or project learned file specified by the skill, repeatable ' +
  'procedures -> a skill). State what you verified and saved.'

// After the built-in runtime contexts.
const REMINDER_ORDER = 10_000

export function apply(ctx) {
  const { name: skillName, description, body } = parseFrontmatter(
    readFileSync(SKILL_MD, 'utf8'),
  )
  ctx.skills.register({
    name: skillName,
    description,
    content: body,
    source: SOURCE,
  })

  // Optional dependency (cordis tutorial ch.3): probe instead of `inject`, so the
  // plugin still loads in profiles without the system-prompt service.
  const systemPrompt = ctx.get?.('systemPrompt')
  systemPrompt?.context({
    name: 'self-improving-loop:reminder',
    order: REMINDER_ORDER,
    text: REMINDER,
    interpolate: false,
  })
}
