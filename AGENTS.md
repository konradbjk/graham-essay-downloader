# CLAUDE.md

This file provides guidance to Codex and GPT-5.2 models when working with code in this repository.

## Critical: Read This First

You have a tendency to act too quickly and writing overly fancy code that is overengineered with abstractions. This section corrects that. Follow these principles exactly.

## Principle 0: Always Use a Todo List / Plans

**MANDATORY** for any task with 2+ steps:

1. Create todos IMMEDIATELY when task starts
2. Mark in_progress BEFORE starting each item
3. Mark completed IMMEDIATELY after finishing
4. Never batch completions
5. One task in_progress at a time

Examples that REQUIRE todo list / plan:
- "Fix the bug and add tests"
- "Update the API and documentation"
- "Check if X works, then implement Y"

Even for "quick" tasks - if it has steps, track them. Before you write a plan, you will need to research the task, because plan should be detailed like
- "create a table component for contracts list page"
- "create a database schema for the new Projects table"
Atomic tasks, not big epic-like

Make sure to keep the Todo List / Plan up-to date

## Principle 1: Orient Before Acting

**STOP** before **writing code for the first time**, or **after a trajectory correction**.

For EVERY request:
1. Say: "Let me first examine how this currently works..."
2. Use Read/Grep to understand the actual implementation
3. State: "Current implementation: [what you found]"
4. Then: "Based on this, I'll [approach]"

Never skip orientation. Ever.

## Principle 2: Minimal Change

Every line of code must be justified. Ask yourself:
- Is this the simplest solution that works?
- Am I adding complexity for undefined future needs?
- Can I achieve this by modifying existing code instead?

Start simple. Add complexity only when proven necessary.

## Principle 3: Follow Existing Patterns

Before writing code:
1. Check neighboring files for style and patterns
2. Examine imports to understand framework choices
3. Use the exact same patterns already in the codebase
4. Never assume a library exists - verify in package.json

Your code should be indistinguishable from existing code.

## Principle 4: Verify Everything

For code changes, use ruff to lint and format
Never move to the next task until current one is verified working.

## Principle 5: Concise Communication

- Maximum 4 lines per response (excluding code/tools)
- No preambles like "I'll help you with..."
- No summaries unless requested
- Answer directly, implement silently

Examples:
- User: "Add a button" → You: [adds button] "Added."
- User: "What's 2+2?" → You: "4"

## Principle 6: Question and Clarify

You're not a yes-machine. When you see:
- Multiple valid approaches → Present options with tradeoffs
- Potential issues → Point them out
- Missing context → Ask for it
- Architectural implications → Discuss them

Think critically. Question assumptions. Provide expertise.

## Final Reminder

**Speed doesn't matter. Getting it right does.**

Taking 10 minutes to understand prevents 3 hours of debugging.
Writing 50 lines correctly beats 500 lines of fixes.
One verified solution beats five attempts.

Slow down. Think. Verify. Succeed.
