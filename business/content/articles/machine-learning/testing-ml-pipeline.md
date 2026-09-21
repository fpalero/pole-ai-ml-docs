# Testing an ML Pipeline Honestly

**Section:** Machine Learning

## What it delivers
A data pipeline that stays testable even when every stage talks to
infrastructure — confidence that a change won't silently break training.

## How it's built
fakeredis and mongomock substitute external stores, `.keras` pipelines get
stubbed, integration suites skip heavy training, and an 80% coverage gate
keeps it honest.

## Proof
- **Code:** [packages/pole-train-model](https://github.com/fpalero/pole-ai-ml/tree/develop/packages/pole-train-model)
- **Live in the pole app:** ~549 tests, 81%+ coverage on the ML package
