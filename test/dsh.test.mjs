// Smoke test for the DSH cordis plugin with a mock ctx (no DSH runtime needed).
import assert from 'node:assert/strict'
import { test } from 'node:test'
import * as plugin from '../lib/index.js'

test('registers the self-improve skill', () => {
  const skills = []
  plugin.apply({ skills: { register: (s) => skills.push(s) } })
  assert.equal(skills.length, 1)
  assert.equal(skills[0].name, 'self-improve')
  assert.ok(skills[0].content.length > 200)
  assert.ok(!skills[0].content.startsWith('---'))
  assert.ok(skills[0].content.includes('~/.self-improving-loop/projects/<project-id>/LEARNED.md'))
  assert.ok(skills[0].content.includes('gitlab.com/team/backend/payments'))
  assert.ok(skills[0].content.includes('bitbucket.org/team/payments'))
  assert.ok(skills[0].content.includes('git config --local --get self-improving-loop.project-id'))
  assert.ok(skills[0].content.includes('Read legacy files only for an explicit migration or memory audit.'))
  assert.ok(skills[0].content.includes('- `~/LEARNED.md`'))
})

test('adds the reminder context when systemPrompt is mounted', () => {
  const contexts = []
  const ctx = {
    skills: { register() {} },
    get: (n) => (n === 'systemPrompt' ? { context: (c) => contexts.push(c) } : undefined),
  }
  plugin.apply(ctx)
  assert.equal(contexts.length, 1)
  assert.equal(contexts[0].text, plugin.REMINDER)
  assert.ok(contexts[0].text.includes('shared or project learned file specified by the skill'))
  assert.equal(contexts[0].interpolate, false)
})

test('loads without systemPrompt service', () => {
  assert.doesNotThrow(() => plugin.apply({ skills: { register() {} }, get: () => undefined }))
})
