#!/usr/bin/env node
// Keeps every platform manifest on the package.json version.
//   node scripts/sync-version.mjs          write package.json version everywhere
//   node scripts/sync-version.mjs --check  exit 1 if any manifest differs
import { readFileSync, writeFileSync } from 'node:fs'

const check = process.argv.includes('--check')
const version = JSON.parse(readFileSync('package.json', 'utf8')).version
const JSON_FILES = ['.claude-plugin/plugin.json', '.codex-plugin/plugin.json', '.cursor-plugin/plugin.json']
const YAML_FILES = ['.hermes-plugin/plugin.yaml']
const bad = []

for (const file of JSON_FILES) {
  const text = readFileSync(file, 'utf8')
  const current = JSON.parse(text).version
  if (current === version) continue
  bad.push(`${file}: ${current}`)
  if (!check) writeFileSync(file, text.replace(/("version"\s*:\s*")[^"]*(")/, `$1${version}$2`))
}
for (const file of YAML_FILES) {
  const text = readFileSync(file, 'utf8')
  const current = (/^version:\s*(.+)$/m.exec(text) || [])[1]?.trim()
  if (current === version) continue
  bad.push(`${file}: ${current}`)
  if (!check) writeFileSync(file, text.replace(/^version:.*$/m, `version: ${version}`))
}

if (bad.length && check) {
  console.error(`Version mismatch (package.json = ${version}):\n  ${bad.join('\n  ')}\nRun: npm run version:sync`)
  process.exit(1)
}
console.log(bad.length ? `Synced to ${version}: ${bad.join(', ')}` : `All manifests at ${version}`)
