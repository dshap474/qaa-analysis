**Rewriting Playbook Formatting**

Okay, the user wants me to rewrite the document because the formatting was bad. I’m guessing this might involve issues like inconsistent bullet points, headings, or perhaps poor spacing in the Markdown. Since they want a full rewrite, I’ll focus on improving the structure. I’ll avoid adding anything extra, just reorganizing the content for better flow and clarity. I'll make sure everything is aligned and easy to read without needing any external tools for this.

**Improving Markdown Formatting**

Okay, the user wants a rewrite with better formatting, and I think I need to adjust a few things to make this look cleaner:

1. I'll adequately space out headings using consistent levels (#, ##, ###).
2. Bullet points should be neat with correct indentation.
3. Adding tables for organized data, with proper markdown formatting.
4. I think I should remove triple backticks around the entire document so it displays more clearly and without causing line breaks in ChatGPT.

I'll make sure there are no formatting issues from the previous mistakes as I organize sections like Mission, Adopt, etc.


Thought for 28 seconds


# Cursor Rules Playbook

**Mission** — Provide concise, high-signal rules that keep Cursor’s Agent precise while minimising token usage.

---

## 1 · Adopt the Modern Rule System

| Choice                                    | Why it matters                                           |
| ----------------------------------------- | -------------------------------------------------------- |
| **Project rules** (`.cursor/rules/*.mdc`) | Version-controlled, repo-scoped, override legacy rules   |
| **User rules** (Settings → Rules)         | Persist across projects; ideal for personal tone & prefs |
| **Avoid legacy `.cursorrules`**           | Deprecated—migrate to per-file MDC                       |

---

## 2 · Layer Rules for Targeted Context

| Layer                         | Trigger                            | Max lines |
| ----------------------------- | ---------------------------------- | --------- |
| **Global “Always”**           | Injected in every prompt           | ≤ 200     |
| **Directory “Auto-Attached”** | File matches `globs`               | ≤ 300     |
| **“Agent Requested”**         | Pulled in by `@ruleName` or intent | ≤ 200     |
| **Manual**                    | One-off templates / generators     | small     |

> Use precise globs (e.g. `src/components/**`) to avoid accidental injections.

---

## 3 · Operational Hygiene & Automation

* Store rules in Git; review via standard PR flow.
* **CI guard** (example):

```yaml
# .github/workflows/validate-cursor-rules.yml
name: Lint Cursor Rules
on: [pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npx cursor-rules-lint .cursor/rules --max-lines 500
```

* Fail the build if a rule exceeds **500 lines** or references missing templates.
* Predictable filenames: `always-global.mdc`, `auto-ui-components.mdc`, etc.
* Link to authoritative docs: [https://docs.cursor.sh/editor-rules](https://docs.cursor.sh/editor-rules).

---

## 4 · Write Effective MDC Rules

```mdc
description: Enforce React component conventions
globs: ["src/components/**/*.tsx"]
alwaysApply: false          # true → Global “Always”

Component Standards
- Functional components with TypeScript generics.
- Props interface at top; export component by name.
- Tailwind for styling; Framer Motion for animation.
@component-template.tsx
```

**Authoring checklist**

* Use imperative bullets (“Early returns for errors”).
* ≤ 500 lines per rule; include one concise example/template.
* Make guidance testable (“Run `npm test` after multi-file edits”).
* Reuse rules; avoid duplicating style docs.

---

## 5 · High-Risk Guard-Rails ⭐

| Guard-rail                               | Enforcement hint                                 |
| ---------------------------------------- | ------------------------------------------------ |
| **Never edit generated assets**          | Deny-list `dist/**`, `migrations/**`             |
| **Protect secrets**                      | Forbid plaintext keys & `.env` files             |
| **Run tests before finalising**          | `npm test` / `pytest` after Agent edits          |
| **Stay idempotent**                      | Prefer additive edits; delete only if tests pass |
| **Block destructive ops outside `src/`** | Deny by default; allowlist as needed             |

---

## 6 · Tighten the Feedback Loop

1. Watch the **Context** panel to confirm injected rules.
2. Commit Agent diffs to a scratch branch; reviewers cherry-pick safe commits.
3. When an error recurs, capture the fix as a new rule.
4. Hold rule retrospectives in PR descriptions.

---

## 7 · Template Library (optional)

```
.cursor/
├── rules/
│   └── auto-ui-components.mdc
└── templates/
    ├── component-template.tsx
    └── api-handler.ts
```

Reference with `@component-template.tsx` to save tokens and guide scaffolding.

---

## 8 · Quick Reference Checklist

* `.cursor/rules` present in Git.
* One global **Always** rule (≤ 200 lines).
* Directory-specific **Auto-Attached** rules with tight globs.
* Optional **Agent Requested** rules for advanced tasks.
* Guard-rails cover generated code, tests, secrets, destructive ops.
* CI: each rule ≤ 500 lines; all templates resolve.
* Rules reviewed like code; issues trigger rule updates.

---

*Follow this playbook to keep Cursor’s Agent on-track, enforce conventions, and avoid prompt bloat—while shipping code with confidence.*
