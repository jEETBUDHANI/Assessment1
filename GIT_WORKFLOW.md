# GitHub Workflow Guide for Assessment

This guide documents the strict branching strategy and Git workflow required for this assessment.

## 1. Initial Setup

### Create Repository
```bash
# Initialize git in your workspace
git init
git add .
git commit -m "chore: initial project scaffold"
git branch -M main

# Or clone an existing repo:
git clone <your-github-url>
cd assessment
```

### Add GitHub Remote
```bash
git remote add origin https://github.com/YOUR_USERNAME/assessment.git
git push -u origin main
```

---

## 2. Feature Branch Workflow

### Pattern: `feature/<descriptive-name>` or `bugfix/<issue-summary>`

### Step 1: Create Feature Branch
**Always branch from `main`**

```bash
git checkout main
git pull origin main
git checkout -b feature/alert-dashboard
```

**Branch naming examples:**
- `feature/alert-dashboard` ← For new features
- `feature/data-model` ← For new components
- `bugfix/fix-timezone-parsing` ← For bug fixes
- `feature/telemetry-chart` ← For UI components

### Step 2: Make Changes & Commit

```bash
# Make your code changes locally
# Save the file...

# Stage changes
git add src/my_file.py

# Commit with conventional commit message
git commit -m "feat: implement alert dashboard status display"
```

**Conventional Commit Format:**
```
<type>: <description>

<optional detailed explanation>
```

**Valid types:**
- `feat:` → New feature
- `fix:` → Bug fix
- `refactor:` → Code restructuring (behavior unchanged)
- `test:` → Add/update tests
- `docs:` → README, documentation, comments
- `chore:` → Dependencies, config files, build changes
- `style:` → Code formatting (whitespace, semicolons, etc.)

**Good commit examples:**
```
feat: create TelemetryReading and Substation dataclasses

This implements the core data model with validation in __post_init__()
and computed status property. Addresses MVP requirement for type safety.

fix: handle missing timezone in log parsing

Previously assumed UTC; now explicitly converts to system timezone
to prevent display drift on different machines.

test: add unit tests for status computation

Covers all three status paths (OK, WARNING, CRITICAL) with edge cases.

docs: add data model design documentation

Explains why we use dataclasses and computed properties instead of
mutable state.
```

**Bad commit examples:**
```
wip                          # ← No type, vague
updated stuff                # ← Not descriptive
i fixed the bug              # ← Lowercase, informal
EVERYTHING IS DONE           # ← All caps, no specificity
```

### Step 3: Push to GitHub
```bash
git push origin feature/alert-dashboard
```

**First push might need:**
```bash
git push -u origin feature/alert-dashboard
```

### Step 4: Create Pull Request (PR)
In GitHub UI:
1. Go to your repository
2. Click "Pull requests" tab
3. Click "New pull request"
4. Base: `main` ← Target
5. Compare: `feature/alert-dashboard` ← Your branch
6. Fill in PR title and description:

```
Title: Add real-time alert dashboard widget

Description:
Implements the core alert dashboard showing substations sorted by severity.

- Displays critical failures first (color-coded red)
- Shows warning states in yellow
- OK devices in green
- Can click to drill into device details

Related to MVP requirement #1 (alert dashboard)
```

7. Click "Create pull request"

### Step 5: Code Review & Merge
- Request a review (if working with others)
- After approval, merge via GitHub UI
- Use "Squash and merge" to keep history clean (optional)
- Delete the branch after merging

```bash
# After merging via GitHub UI, update locally:
git checkout main
git pull origin main
git branch -d feature/alert-dashboard  # Delete local branch
```

---

## 3. Workflow Diagram

```
                          feature/alert-dashboard
                          ↓
main ←─────────────────────┘  (Pull Request + Merge)
  ↓
  ├─ commit: "feat: implement alert dashboard"
  ├─ commit: "test: add dashboard unit tests"
  ├─ commit: "fix: handle empty data case"
  └─ commit: "docs: update README with UI architecture"
```

---

## 4. Example: Complete Feature from Start to Finish

### Scenario: Add a chart showing telemetry trends

**Step 1: Start feature branch**
```bash
git checkout main
git pull origin main
git checkout -b feature/telemetry-chart
```

**Step 2: Create chart implementation**
```bash
# Edit src/ui/detail_view.py
# ... implement matplotlib chart code ...
git add src/ui/detail_view.py
git commit -m "feat: add time-series chart widget

Displays voltage, temperature, and load trends over 24 hours.
Uses matplotlib embedded in PyQt5 canvas for interactive plotting.
Allows user to hover for specific values."
```

**Step 3: Add unit tests**
```bash
# Edit tests/test_ui.py
# ... write tests for chart rendering ...
git add tests/test_ui.py
git commit -m "test: add unit tests for telemetry chart

Tests chart rendering with various data scenarios:
- Normal data (24 hour history)
- Single point (minimal data)
- Missing values (handles gracefully)"
```

**Step 4: Update documentation**
```bash
# Edit README.md, ARCHITECTURE.md
git add README.md docs/ARCHITECTURE.md
git commit -m "docs: explain telemetry chart design

Updates Architecture section with chart design rationale and
matplotlib integration approach."
```

**Step 5: Push and PR**
```bash
git push -u origin feature/telemetry-chart
```

Then create PR on GitHub UI → Review → Merge → Delete branch

---

## 5. Common Git Commands

```bash
# View branch status
git status

# List all branches (local)
git branch

# List remote branches
git branch -r

# Switch to different branch
git checkout main

# Create AND switch to new branch
git checkout -b feature/my-feature

# View commit history
git log --oneline -10

# View changes before commit
git diff src/file.py

# View changes in staging area
git diff --staged

# Undo unstaged changes
git checkout src/file.py

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Revert to last commit (discard changes)
git reset --hard HEAD

# Pull latest with conflict resolution
git fetch origin
git pull origin main
```

---

## 6. Troubleshooting

### Merge Conflicts
```bash
# If PR has conflicts:
git checkout feature/your-branch
git merge main  # Bring in latest main
# Fix conflicts in your editor
git add .
git commit -m "merge: resolve conflicts with main"
git push origin feature/your-branch
```

### Wrong Branch?
```bash
git checkout main  # Switch to main
# Start over with correct branch name
```

### Forgot to Create Branch (committing to main)?
```bash
# Undo last commit but keep changes
git reset --soft HEAD~1

# Create new branch with those changes
git checkout -b feature/correct-name

# Commit again
git add .
git commit -m "feat: descriptive message"
```

---

## 7. Assessment Checklist

- [ ] GitHub repo created and linked
- [ ] `.gitignore` committed
- [ ] `main` branch is default
- [ ] All work on feature branches
- [ ] Each PR has clear description
- [ ] Commits follow conventional format
- [ ] No direct commits to `main` (all via PR)
- [ ] Final PR merged with video link in description

---

## Questions?

Review examples in `/ASSESSMENT_PLAN.md` section 4 for more details.
