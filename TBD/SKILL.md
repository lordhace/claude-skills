---
name: "ado-test-cases"
description: Generate Azure DevOps Test Plan test cases from a JIRA ticket's Acceptance Criteria, output as an importable CSV. Use this whenever the user supplies a JIRA ticket, a set of acceptance criteria, or asks to "write test cases," "create test cases," "make a test plan," or produce an ADO/Azure DevOps test case file — even if they don't explicitly say "Azure DevOps" or "CSV." Trigger on any request to turn requirements or acceptance criteria into structured test cases.
---

# ADO Test Cases from JIRA Acceptance Criteria

Turn the Acceptance Criteria of a JIRA ticket into Azure DevOps (ADO) Test Plan
test cases, delivered as a CSV that imports cleanly into ADO Test Plans.

## Workflow

1. **Read the Acceptance Criteria.** Pull the acceptance criteria from the supplied
   JIRA ticket (pasted text, a screenshot, or a description). Each distinct,
   independently-verifiable behavior becomes one test case. The same applies if
   the JIRA URL(s) provided reference **multiple JIRA tickets** (including a JQL
   filter/search URL that resolves to a list of tickets) — pull the Acceptance
   Criteria from each ticket and generate test cases for each one.
2. **Design the test cases.** For each test case decide a clear title and an ordered
   list of steps. Each step has an **Action** (what the tester does) and an
   **Expected** result (what should happen). Cover the happy path plus the negative
   and edge cases implied by the criteria. Keep every test case attributed to the
   single JIRA ticket it came from — never merge test cases from different tickets
   into one list at this stage.
3. **Check for duplicate or repeating test cases before writing the spec.**
   As you assemble each ticket's test case list, watch for:
   - **Duplicate titles** — the same behavior written up twice, often from
     re-reading overlapping AC bullets (e.g. a shared "the modal opens
     consistently across create/edit/view" check restated once per AC item
     instead of covered by one test case).
   - **Repeating scripts under different titles** — two test cases with
     different names but the same steps in the same order, usually from
     copy-pasting one test case as a starting point for a similar one and
     forgetting to change the body.
   - **Cross-ticket repeats** — when generating for multiple tickets in one
     request, the same generic check (e.g. read-only users see labels, not
     editable fields) reappearing verbatim across tickets is fine *if* it's
     genuinely required by each ticket's own AC — but don't pad a ticket's
     list by reusing another ticket's test case just to fill it out.

   Merge or remove duplicates so each distinct, independently-verifiable
   behavior is tested exactly once. `scripts/generate_csv.py` also enforces
   this as a hard backstop — it refuses to write a CSV (and reports the exact
   titles involved) if the spec still contains a duplicate title or an
   identical step sequence under two titles — but treat that as a safety net,
   not the primary check; do the dedup pass yourself before generating.
4. **Generate one CSV per JIRA ticket.** When the request covers **multiple
   tickets**, each ticket gets its **own JSON spec and its own CSV file** — never
   combine test cases from different tickets into a single CSV. This is what makes
   each file import into ADO as its own Test Plan. When there is only **one**
   ticket, a single CSV is still correct. Write each ticket's test cases to its own
   JSON spec and run `scripts/generate_csv.py` once per ticket. Do **not**
   hand-format the CSV — the script guarantees the column layout, row structure,
   quoting, and duplicate-freedom are correct every time. If it exits with a
   duplicate-test-case error, fix the spec (merge/remove the offending test
   case) and re-run — don't work around it by renaming a title just to dodge
   the check.
5. **Verify and deliver.** For each ticket, confirm the script reported the
   expected row count and that every row is 11 columns. Present **all** resulting
   `.csv` files to the user (one per ticket), and briefly list which file
   corresponds to which JIRA ticket.

## Output format

ADO Test Case CSV — **exactly 11 columns**, in this order:

`ID, Work Item Type, Title, State, Assigned To, Area, Iteration Path, Tags, Test Step, Step Action, Step Expected`

The file has a column-header row, then for each test case a **TC header row**
followed by one **step row** per step.

**TC header row** (the test case itself):
- `ID` — empty
- `Work Item Type` — `Test Case`
- `Title` — the test case title, written **verbatim** (see Title rules)
- `State`, `Assigned To`, `Area`, `Iteration Path`, `Tags` — filled with the standard field values
- `Test Step`, `Step Action`, `Step Expected` — **empty**

**Step row** (one per step, immediately under its TC header row):
- The first **8 fields are empty** (`ID` through `Tags`)
- `Test Step` — the step number (1, 2, 3, …)
- `Step Action` — what the tester does
- `Step Expected` — the expected result

## Multiple tickets → separate files, one per Test Plan

Each JIRA ticket becomes its **own standalone CSV** — never one merged file
covering several tickets. This is the difference between "one Test Plan" and
"several Test Plans" on import.

- **File naming:** `<TICKET-KEY>_test_cases.csv`, e.g. `WEB-12461_test_cases.csv`,
  `WEB-12495_test_cases.csv`. If the user names a plan explicitly, you may use
  `<TICKET-KEY>_<plan-name>.csv` instead.
- **One spec, one CSV, per ticket:** build a separate JSON spec per ticket
  (only that ticket's test cases) and invoke `scripts/generate_csv.py` once per
  ticket, writing to that ticket's own output path. Do not accumulate test cases
  from multiple tickets into one spec file.
- **Delivery:** present every generated `.csv` to the user, and map each file
  name to its JIRA ticket key/summary so it's obvious which file is which
  ticket's Test Plan.
- If the user explicitly asks for one combined file instead (e.g. "put them all
  in one CSV"), that overrides this default — but the default behavior is always
  one file per ticket.

## Standard field values

Use these unless the user overrides them:

| Field | Value |
|---|---|
| State | `Design` |
| Assigned To | `Leochard Catipay` |
| Area | `Clockworks Applications` |
| Iteration Path | `Clockworks Applications\Software 09-09-26 to 09-29-26` |
| Tags | `TBD` |

Notes that are easy to get wrong:
- The metadata column is **`Area`**, not "Area Path".
- There is **no Priority field** — do not add one.

## Title rules

- Write the title **directly** — no `TC-` prefix and no numbering in the title text.
- A title containing a pipe `|` **must be quoted** in the CSV (the script handles this).
- Include a reference to the specific Acceptance Criteria item the test case verifies
  (e.g. `AC#1`, `AC#1.a`), matching however the ticket numbers its AC. Append it to the
  end of the title, e.g. `Verify successful login with valid credentials (AC#1)`.

## Quoting rules (QUOTE_MINIMAL + pipe)

- Quote a field **only** when its value contains a comma `,`.
- Additionally, quote any value containing a pipe `|`.
- (Embedded quotes and newlines are also quoted/escaped automatically.)
- The Iteration Path value has a backslash but no comma, so it is **not** quoted.

The `generate_csv.py` script applies all of these — don't second-guess it by quoting manually.

## Using the generator

Write a JSON spec like this:

```json
{
  "test_cases": [
    {
      "title": "Verify successful login with valid credentials",
      "steps": [
        {"action": "Navigate to the login page", "expected": "Login page is displayed"},
        {"action": "Enter a valid username and password", "expected": "Credentials are accepted"},
        {"action": "Click the Login button", "expected": "User is redirected to the dashboard"}
      ]
    }
  ]
}
```

To override the standard values for a run, add an optional `"fields"` object
(`state`, `assigned_to`, `area`, `iteration_path`, `tags`).

Then run:

```bash
python scripts/generate_csv.py spec.json test_cases.csv
```

The script verifies every row is 11 columns and reports the row count.

**When multiple tickets are in scope**, repeat this per ticket instead of writing
one shared spec — one spec file and one CSV per ticket, e.g.:

```bash
python scripts/generate_csv.py WEB-12461_spec.json WEB-12461_test_cases.csv
python scripts/generate_csv.py WEB-12495_spec.json WEB-12495_test_cases.csv
python scripts/generate_csv.py WEB-12483_spec.json WEB-12483_test_cases.csv
```

Check the row count the script reports for each file, then present all of the
resulting `.csv` files to the user (see "Multiple tickets → separate files,
one per Test Plan" above).

## Example

**Input (acceptance criteria):** "User can reset their password via the 'Forgot
password' link; an email with a reset link is sent; the link expires after 24 hours."

**Resulting CSV (illustrative):**

```
ID,Work Item Type,Title,State,Assigned To,Area,Iteration Path,Tags,Test Step,Step Action,Step Expected
,Test Case,Verify password reset email is sent,Design,Leochard Catipay,Clockworks Applications,Clockworks Applications\Software 09-09-26 to 09-29-26,TBD,,,
,,,,,,,,1,Click the Forgot password link,Password reset page is displayed
,,,,,,,,2,Enter a registered email and submit,Confirmation message is shown
,,,,,,,,3,Check the inbox,A reset email with a link is received
```

(The TC header row carries the title and metadata; each step row leaves the first
8 fields empty and fills the last 3.)
