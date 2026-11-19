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
  assert.equal(contexts[0].interpolate, false)
})

test('loads without systemPrompt service', () => {
  assert.doesNotThrow(() => plugin.apply({ skills: { register() {} }, get: () => undefined }))
})
