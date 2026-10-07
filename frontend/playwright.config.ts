import { defineConfig } from '@playwright/test'

// UI QA agent (roadmap step 3): drives the real dashboard in a headless
// browser and checks it actually works end to end, against real exported
// data -- not mocked. Pass/fail is always a deterministic assertion here;
// see ops/ui_qa_diagnose.py for the one place an LLM is allowed to comment
// on a failure (explain, never decide).
export default defineConfig({
  testDir: './tests',
  timeout: 30_000,
  retries: 0,
  reporter: [['list'], ['json', { outputFile: 'tests/results/results.json' }]],
  use: {
    baseURL: 'http://localhost:5173',
    screenshot: 'on',
    trace: 'retain-on-failure',
  },
  outputDir: 'tests/results/artifacts',
  webServer: {
    command: 'npm run dev -- --port 5173 --strictPort',
    url: 'http://localhost:5173',
    reuseExistingServer: !process.env.CI,
    timeout: 60_000,
  },
})
