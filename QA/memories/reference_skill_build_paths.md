---
name: reference-skill-build-paths
description: Two-folder skill build convention — where skill sources are edited and where packaged .skill files go
version: 1.0
source: https://bitbucket.org/kgsbuildings/skillfiles/src/master/QA/memories/
metadata:
  type: reference
---

Skill work uses **two sibling folders** under the user's Claude working
directory. The names below are this team's defaults; the *roles* are what
matter and do not change.

- **`skills-source/<skill-name>/`** — the editable source. Every `SKILL.md`
  and `references/` edit goes here. This is the source of truth.
- **`skills-dist/<skill-name>.skill`** — the packaged output. Package into
  this **existing** folder. Do not create a new `dist/`, and do not use the
  governance skill's `/mnt/user-data/outputs/`, which is a Linux sandbox
  path that does not exist on a Windows machine.

**Both stay in sync.** A packaged `.skill` that no longer matches its
`skills-source/` copy is a silent trap — the installed skill and the
reviewable source disagree, and the next edit is made against the wrong
one. Any change to a skill means editing the source *and* repackaging into
dist, not one or the other.

Packaged filename must exactly match the source folder name, with **no
version suffix**, so it cleanly overwrites the installed copy.
`skills-dist/` is typically not under git, so packaging replaces the prior
build rather than versioning it — the skill's own
`references/CHANGELOG.md` is the audit trail.

## This machine's actual paths are NOT in this file

This file is shared across machines, so it holds no absolute paths. Those
live in a separate local memory, **`reference-skill-folder-config`**, which
is personal to each machine and is never overwritten when this file is
updated.

Before any skill packaging work:

1. Look for a memory named `reference-skill-folder-config`. If it exists,
   use the paths it records and proceed.
2. If it does not exist, ask the user:
   - the full path to their Claude working directory
     (e.g. `C:\Users\<you>\OneDrive - <Org>\Documents\claude`)
   - their source and dist folder names, defaulting to `skills-source`
     and `skills-dist` unless they say otherwise
3. **Verify both folders exist** before packaging — do not create them
   silently.
4. Write the confirmed values to a new `reference-skill-folder-config`
   memory using the shape below, and add a line for it in `MEMORY.md`.

Never guess these paths from another user's memory, from this file's
examples, or from the governance skill's built-in defaults.

Shape of the local config memory:

```markdown
---
name: reference-skill-folder-config
description: This machine's Claude working directory and skill source/dist folder names
metadata:
  type: reference
---

Confirmed <date>:

- Working directory: `<full path>`
- Source folder: `<name>` → `<full path>`
- Dist folder: `<name>` → `<full path>`

Personal to this machine. Not shared, and not overwritten by updates to
[[reference-skill-build-paths]].
```

---

Check this before choosing an output path; the packaging instructions in
`anthropic-skills:skill-governance` assume a Linux sandbox and its paths do
not map to Windows.

Companion memories: [[reference-package-skill-windows-encoding]] (the
UTF-8 flag the packager needs on Windows) and
[[feedback-skill-install-definition]] (when a skill counts as installed,
and what that means for CHANGELOG entries).
