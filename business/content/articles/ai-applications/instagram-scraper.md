# Scraping Instagram at Scale

**Section:** AI Applications

## What it delivers
A data-acquisition pipeline that survives rate limits and session rot — so your
training data keeps flowing without getting blocked.

## How it's built
Authenticated sessions with CSRF and sessionid cookies, anti-bot waits,
DiskWriter persistence, and a QC loop that keeps scraped posts safe before use.

## Proof
- **Code:** [packages/pole_crawler](https://github.com/fpalero/pole-ai-ml/tree/develop/packages/pole_crawler)
- **Live in the pole app:** feeds the training dataset pipeline
