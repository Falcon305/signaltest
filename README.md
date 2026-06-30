# signaltest

Regression tests for LLM agents that don't fail your CI on noise.

LLMs are non-deterministic, so naive eval checks flake: a score drifts a point on
randomness, CI goes red, and the team stops trusting it. signaltest runs each case
several times and blocks a PR only when a regression is statistically real, not
noise — then shows a diff of what actually changed in the agent's run.

Local-first. No account, no data leaves your repo.

Status: early, v0.1 in progress.

## License

MIT
