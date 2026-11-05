// self-improving-loop — DSH cordis plugin.
// Registers the bundled "self-improve" skill into the DSH skill registry so it
// appears in the session skill catalog and is loadable via the `skill` tool.
// The same skills/self-improve/SKILL.md is shared by every platform adapter
// (Claude Code / Codex / Cursor / Hermes) — one source of truth.
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
}
