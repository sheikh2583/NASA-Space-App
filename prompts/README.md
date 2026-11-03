# Prompt packs

> Disclaimer: no AI tool has run these prompts. Results vary by tool; review every diff and rely on the tests and docs/VERIFY.md checks (docs/KNOWN_GAPS.md item 12).

One file per person. Each file is a sequence of prompts that together build your whole workstream.

How to use
1. Open one AI chat for your workstream. Paste docs/AI_PREAMBLE.md first.
2. Paste the prompts in order, one at a time. Each has: When, Inputs, the prompt text, Output, Test.
3. Do not start the next prompt until the Test of the current one passes.
4. When an Output is a hand-off (marked HANDOFF), post the message from docs/HANDOFF_TEMPLATE.md.
5. Unclear? Use the stated default, note the assumption in your NOTES.md, move on.
6. Run every prompt's output on a small slice first (one region, one year).

## Phase prompts
For each phase of the build there is one agent prompt per person in prompts/phases/. Paste prompts/phases/00_agent_loop.md first, then the prompt for the current phase; it names the numbered prompts above that supply the detail.
