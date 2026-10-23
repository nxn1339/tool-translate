---
name: techlead-pr-review
description: Use when reviewing pull requests that must match documented dev tasks, DoD, branch scope, verification evidence, and merge readiness across app and docs repositories.
---

# Tech Lead PR Review

## Overview

Review PRs like a Tech Lead: map each PR to documented `DEV-XXX` tasks, verify scope and DoD, inspect code risk, run or require evidence, then give merge/block comments.

This skill is for app/docs split repos where the source of truth lives in docs and code lands through PRs. It works well for Smile-style repos but can adapt to any `dev_task_list.md` plus app repo.

## Core Workflow

1. Resolve repos and branch:
   - App repo: code under review.
   - Docs repo: task source of truth.
   - Base branch: default `develop`.
   - Prefer SSH remotes such as `git@github-company:Smile-Software/...`.
2. Collect context:
   - Use `scripts/collect-pr-review-context.ps1` when on Windows/PowerShell.
   - If `gh` is missing, fetch PRs via `refs/pull/<number>/head`.
   - Read task rows from `docs/01.management/04.task/dev_task_list.md`.
3. Map PR to tasks:
   - Identify owner, dependency, DoD, forbidden scope, and verification commands.
   - Backend foundation usually maps to backend `DEV-*`; mobile foundation maps to mobile `DEV-*`.
   - Never accept "looks fine" without task mapping.
4. Review in this order:
   - Findings first: bugs, merge blockers, missing tests, security/privacy, broken build.
   - Scope guard: no real feature behavior when task says foundation-only.
   - DoD match: every task claim has code or evidence.
   - Verification: commands pass, missing CI job noted, local-only evidence called out.
   - Standards: `git diff --check`, formatting, lint coverage, docs/source-of-truth boundaries.
5. Output:
   - PR number, branch/ref, mapped tasks.
   - Findings with severity and file/line when possible.
   - Required fixes before merge.
   - Checks to rerun after fixes.
   - Merge recommendation: `merge`, `merge after fixes`, or `block`.

## Collector Script

Run:

```powershell
# In workspace (.agents):
.agents\skills\techlead-pr-review\scripts\collect-pr-review-context.ps1 `
  -AppRepo F:\SmileProject\WishListProject\Src\smile-wishlist-app `
  -DocsRepo F:\SmileProject\WishListProject\Src\smile-wishlist-docs `
  -PrNumbers 2,5 `
  -Base develop
```

Use output as raw context, not as final judgment. Still inspect risky diffs manually.

## Merge Gate Checklist

| Gate | Pass means |
|---|---|
| Task map | PR maps to exact `DEV-XXX` rows and no required dependency is ignored. |
| Scope | No business feature, endpoint, DB schema, auth flow, storage plugin, or source-of-truth docs change outside task. |
| DoD | Each DoD phrase is either implemented, verified, or listed as blocker. |
| Tests | Required command evidence exists; CI covers the touched platform or gap is blocker/commented. |
| Diff hygiene | `git diff --check` clean; formatting/lint/test output clean. |
| Security | No secret, stack, PII, unbounded request ID echo, auth behavior, or private data exposure. |
| Merge safety | Base branch up to date or PR rebased; conflict and generated-file risk understood. |

## Comment Template

```markdown
Review result: <merge | merge after fixes | block>

Mapped tasks:
- DEV-XXX: <covered/partial/missing>

Required before merge:
- [P?] <file:line> <issue>. Fix: <specific action>.

Checks to rerun:
- <command>

Notes:
- <CI coverage gap, local evidence, or scope guard>
```

## Common Mistakes

- Reviewing code only and skipping `dev_task_list.md`.
- Treating local Flutter evidence as CI coverage.
- Missing `git diff --check` because lint ignores a folder.
- Allowing foundation PRs to add real auth/profile/wishlist behavior.
- Saying "pass" when a command could not be independently verified.
