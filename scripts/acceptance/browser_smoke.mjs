import { chromium, request } from 'playwright'
import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'

const base = process.env.FILEMATE_WEB_URL || 'http://127.0.0.1:5173'
const api = process.env.FILEMATE_API_URL || 'http://127.0.0.1:8001'
const scriptDir = path.dirname(fileURLToPath(import.meta.url))
const repoRoot = path.resolve(scriptDir, '..', '..')
const outDir = process.env.FILEMATE_EVIDENCE_DIR || path.join(repoRoot, '_working', 'browser-acceptance')
fs.mkdirSync(outDir, { recursive: true })

const routes = [
  '/', '/today', '/import', '/classification', '/naming', '/schedule', '/history',
  '/ai-tools', '/study-plan', '/wrongbook', '/interview', '/interview-bank',
  '/growth', '/knowledge'
]

const browser = await chromium.launch()
const page = await browser.newPage({ viewport: { width: 1280, height: 800 } })
const results = []

for (const route of routes) {
  const errors = []
  const onConsole = (m) => { if (m.type() === 'error') errors.push(m.text()) }
  const onPageError = (e) => errors.push(String(e))
  page.on('console', onConsole)
  page.on('pageerror', onPageError)
  try {
    const resp = await page.goto(base + route, { waitUntil: 'domcontentloaded', timeout: 30000 })
    await page.waitForTimeout(800)
    const title = await page.title()
    const mainText = await page.locator('main').innerText().catch(() => '')
    const hasHorizontalOverflow = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth)
    const filename = (route === '/' ? 'home' : route.replace(/\//g, '_').slice(1)) + '.png'
    await page.screenshot({ path: path.join(outDir, filename), fullPage: true })
    results.push({
      route,
      status: resp ? resp.status() : null,
      title,
      hasMainContent: mainText.trim().length > 0,
      hasHorizontalOverflow,
      consoleErrors: errors,
    })
  } catch (err) {
    results.push({ route, status: null, title: '', consoleErrors: errors, error: String(err) })
  } finally {
    page.off('console', onConsole)
    page.off('pageerror', onPageError)
  }
}
await browser.close()

const ctx = await request.newContext({ baseURL: api, timeout: 15000 })
const apiResults = []
for (const ep of ['/api/health', '/sessions', '/knowledge/sources', '/wrongbook', '/review/today', '/study-plans', '/interview/questions', '/analytics/overview', '/evaluation/feedback/summary']) {
  try {
    const r = await ctx.get(ep)
    apiResults.push({ endpoint: ep, status: r.status(), ok: r.ok() })
  } catch (err) {
    apiResults.push({ endpoint: ep, status: null, ok: false, error: String(err) })
  }
}
await ctx.dispose()

const routeFailures = results.filter((item) =>
  item.status !== 200 || item.error || item.consoleErrors.length > 0 || !item.hasMainContent || item.hasHorizontalOverflow
)
const apiFailures = apiResults.filter((item) => !item.ok)
const report = {
  baseline: process.env.FILEMATE_BASELINE || 'local',
  generated_at: new Date().toISOString(),
  passed: routeFailures.length === 0 && apiFailures.length === 0,
  routes: results,
  api: apiResults,
  failures: { routes: routeFailures, api: apiFailures },
}
const out = path.join(repoRoot, '_working', 'browser-acceptance.json')
fs.writeFileSync(out, JSON.stringify(report, null, 2), 'utf-8')
console.log(JSON.stringify(report, null, 2))
if (!report.passed) process.exitCode = 1
