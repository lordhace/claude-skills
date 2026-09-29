---
name: reference-package-skill-windows-encoding
description: package_skill.py crashes on Windows without PYTHONIOENCODING=utf-8
version: 1.0
source: https://bitbucket.org/kgsbuildings/skillfiles/src/master/QA/memories/
metadata:
  type: reference
---

`skill-creator/scripts/package_skill.py` prints a 📦 emoji on its first line.
The Windows console defaults to cp1252, so the script dies with
`UnicodeEncodeError: 'charmap' codec can't encode character '\U0001f4e6'`
before doing any work.

Run it with UTF-8 output instead of editing the vendored script.

Bash / Git Bash:
```bash
cd "<skill-creator dir>" && PYTHONIOENCODING=utf-8 python -m scripts.package_skill "<source path>" "<output dir>"
```

PowerShell (no inline env-var prefix — set it first):
```powershell
$env:PYTHONIOENCODING = 'utf-8'; python -m scripts.package_skill "<source path>" "<output dir>"
```

`scripts/quick_validate.py` takes one argument (the skill path) and has no
emoji, so it runs unmodified. Validate before packaging — the packager also
validates internally, but a separate pass gives a clearer failure.

Source and output paths come from this machine's
[[reference-skill-folder-config]]; see [[reference-skill-build-paths]] for
what those folders are and how to set the config up the first time.
