#!/usr/bin/env node
/* Simple workspace preflight: enforce Node 20, corepack/pnpm presence, optional web env hints */
const cp = require('child_process')

function exec(cmd) {
  try { return cp.execSync(cmd, { stdio: ['ignore','pipe','ignore'] }).toString().trim() } catch { return '' }
}

function fail(msg) { console.error(`Preflight: ${msg}`); process.exit(1) }

// Node version 20.x
const node = process.version
const major = parseInt((node.replace('v','').split('.')[0] || '0'), 10)
if (major !== 20) fail(`Unsupported Node version ${node}. Please use Node 20.x`)

// corepack/pnpm
const pnpmv = exec('pnpm -v')
if (!pnpmv) fail('pnpm not found. Run: corepack enable && corepack prepare pnpm@9 --activate')

// Optional: warn if web API base missing
const fs = require('fs'); const path = require('path')
const envLocal = path.join(__dirname, '..', 'apps', 'web', '.env.local')
if (!fs.existsSync(envLocal)) {
  console.warn('Preflight: apps/web/.env.local not found. Using NEXT_PUBLIC_API_BASE from env or default http://localhost:8010')
}

console.log('Preflight: OK. Node', node, 'pnpm', pnpmv)

