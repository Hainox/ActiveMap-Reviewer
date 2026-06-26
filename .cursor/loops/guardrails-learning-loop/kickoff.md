Start the "Guardrails Learning Loop" loop.

Goal: tests and lint pass without repeating prior failure patterns
Max iterations: 12
Between iterations run: npm test && npm run lint
Exit when: all checks pass

Step 1: Read .ralph/guardrails.md, run checks, and if a failure repeats, add a sign before fixing.

Self-pace this loop. After each iteration, run the check command, read the output, and only continue if the exit condition is not met. Stop when the exit condition passes or max iterations is reached. Give a short status update each pass.

Guardrails (do not skip):
- Do not modify the check command or exit criteria to force success
- Do not skip, disable, or bypass checks to pass the exit condition
- If stuck after several iterations, stop and report blockers instead of gaming metrics