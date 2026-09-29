---
name: feedback-skill-install-definition
description: A skill counts as "installed" only after it's packaged as .skill and installed via the Claude UI — file edits during pre-install review don't warrant new CHANGELOG entries
version: 1.0
source: https://bitbucket.org/kgsbuildings/skillfiles/src/master/QA/memories/
metadata:
  type: feedback
---

Copying skill source files into `C:\Users\<you>\.claude\skills\<name>\` is a
staging step, **not an install**. A skill is only "installed" once it has
been packaged into a `.skill` archive and installed through Claude Code's
Customize → Skills UI (or pushed through org distribution).

**Why:** The governance skill's rule *"Do not modify existing entries. Add
new entries at the top"* on `references/CHANGELOG.md` applies to
post-release history. During pre-install review the initial entry has not
been released and can be amended freely — adding a new entry for every
review-time correction clutters the audit log with pre-release churn.

**How to apply:**

- **Pre-install** (source under review, not yet packaged or installed via
  the UI): amend the initial CHANGELOG entry in place. Do not add new
  entries for corrections found during review.
- **Post-install** (packaged and installed, or shared with teammates):
  append a new CHANGELOG entry at the top for every change. Never edit
  existing entries.

When in doubt about a skill's install state, ask before adding a CHANGELOG
entry.

Packaging mechanics: [[reference-skill-build-paths]] and
[[reference-package-skill-windows-encoding]].
