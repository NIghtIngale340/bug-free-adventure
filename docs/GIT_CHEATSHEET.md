# GIT CHEATSHEET & SAFE WORKFLOW FOR THE TEAM
## Copy-Paste Recipes for Ken, Chester, and Integrator

**Audience:** All Team Members  
**Core Purpose:** Prevents accidental code loss, broken branches, and merge panic.

---

## 1. The Three Golden Git Rules

1. **NEVER commit directly to `main` or `develop`.** Always work on a task branch (`feat/...`).
2. **Never push with `--force` on `main` or `develop`.**
3. **Always pull latest `develop` before starting work each day.**

---

## 2. Daily Morning Routine (Run Before Writing Any Code)

```bash
# 1. Switch to develop and get latest changes
git checkout develop
git pull origin develop

# 2. Switch to your feature branch (e.g. feat/be-005-simulator)
git checkout feat/be-005-simulator

# 3. Rebase your branch on top of latest develop
git rebase develop
```

---

## 3. Starting a New Task

When picking up a new task from the board:

```bash
# 1. Make sure develop is fresh
git checkout develop
git pull origin develop

# 2. Create and switch to your new branch
# Pattern: feat/<role>-<task-id>-<short-description>
git checkout -b feat/be-005-simulator-core

# (For Chester):
# git checkout -b feat/fe-004-simulator-page
```

---

## 4. Saving and Pushing Your Work

Make small, clear commits as you complete sub-features:

```bash
# 1. Check which files were modified
git status

# 2. Stage your files
git add app/core/simulator.py tests/core/test_simulator.py

# 3. Commit with Conventional Commits format
git commit -m "feat(core): implement symbol-by-symbol DFA state traversal"

# 4. Push branch to GitHub (first time)
git push -u origin feat/be-005-simulator-core

# (Subsequent pushes on the same branch):
git push
```

---

## 5. Opening a Pull Request (PR)

1. Go to your repository on GitHub.
2. Click **"Compare & pull request"**.
3. **Base branch:** Select `develop` (DO NOT select `main`).
4. **Compare branch:** Select your feature branch (`feat/...`).
5. **Title format:** `feat(core): implement BE-005 simulator core`
6. **Assign Reviewer:** Select the **Integrator**.
7. In the description, write:
   - What task was completed.
   - Files changed.
   - Proof that tests passed: `pytest tests/core tests/services passed`.

---

## 6. How to Resolve Merge Conflicts (Step-by-Step)

If GitHub reports that your PR has conflicts with `develop`:

```bash
# 1. On your local machine, checkout your feature branch
git checkout feat/fe-004-simulator-page

# 2. Fetch the latest develop branch
git fetch origin

# 3. Start the rebase
git rebase origin/develop

# 4. Git will pause and show conflicting files. Open the files in VS Code / IDE.
# Look for <<<<<<< HEAD, =======, and >>>>>>>.
# Keep the correct lines and delete the Git conflict markers.

# 5. After saving the fixed files, stage them:
git add <conflicted-file-path>

# 6. Continue the rebase (DO NOT run git commit):
git rebase --continue

# 7. Once rebase completes successfully, verify tests:
pytest

# 8. Force-push the resolved branch safely:
git push --force-with-lease
```

---

## 7. Emergency Panic Button (Troubleshooting Common Mistakes)

### Problem 1: "I accidentally committed on develop instead of a feature branch!"
```bash
# 1. Create a new branch with your commits intact:
git branch feat/my-saved-work

# 2. Reset local develop back to match GitHub:
git reset --hard origin/develop

# 3. Switch to your new branch and continue working safely:
git checkout feat/my-saved-work
```

### Problem 2: "I messed up my local branch and want to restart from GitHub!"
```bash
# WARNING: Discards uncommitted local edits on this branch
git reset --hard origin/feat/be-005-simulator-core
```

### Problem 3: "Git says 'You are in detached HEAD state'!"
```bash
# Switch back to your named branch:
git checkout feat/be-005-simulator-core
```

### Problem 4: "I accidentally edited a file and want to undo my changes to it!"
```bash
# Revert a specific file to the last commit:
git checkout -- app/core/models.py
```
