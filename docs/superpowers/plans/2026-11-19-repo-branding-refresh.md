# Repository Branding Refresh Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**Goal:** Rename the public repo and skill to `novel-illustrator`, document Codex and Antigravity use, show two labeled novel illustrations, and ignore generated production runs.

**Architecture:** Keep the skill and Python toolkit at the repository root. Add two source-faithful sample images under `docs/showcase/`, with user-facing captions in the README. Align the GitHub slug, `SKILL.md` front matter, README, and origin URL.

**Tech Stack:** Markdown, Git, GitHub CLI, PowerShell.

**Spec:** `docs/superpowers/specs/2026-11-19-repo-branding-design.md`

## Global Constraints

- README must contain no em dash.
- README must include Codex and Antigravity install locations for user and workspace scope.
- Showcase assets must be copied byte-for-byte from approved Chapter 1 illustrations and labeled with novel and chapter.
- Ignore timestamped production folders and EPUB outputs without ignoring `docs/showcase/` assets.
- Do not modify the Python scripts or the illustration workflow.

## Review Focus

- Every README image path resolves to a tracked showcase file.
- Captions identify the source novel and chapter correctly.
- Ignore rules cover timestamped production folders but leave showcase images trackable.
- Skill name, README name, GitHub slug, and `origin` URL agree.
- README contains no em dash and installation paths match the supported agents.

### Task 1: Prepare the image gallery and ignore rules

**Files:**
- Create: `docs/showcase/first-fifteen-lives-chapter-01.png`
- Create: `docs/showcase/inverted-world-chapter-01.png`
- Modify: `.gitignore`

- [x] Copy the two approved Chapter 1 images byte-for-byte into `docs/showcase/`.
- [x] Replace blanket image ignores with scoped rules for timestamped book runs, temporary work, and EPUB outputs.
- [x] Verify source and showcase file hashes match; verify run folders are ignored and showcase images are not.

### Task 2: Update the skill identity and README

**Files:**
- Modify: `SKILL.md`
- Modify: `README.md`

- [x] Change skill front matter name to `novel-illustrator`.
- [x] Rewrite README sections for the platform-neutral skill, features, Codex and Antigravity installation, Python requirements, CLI workflow, and gallery.
- [x] Label each sample with its novel and chapter; provide descriptive alt text.
- [x] Verify all sample paths exist, README text has no em dash, and documented commands match the scripts' CLI.

### Task 3: Commit and publish the rename

**Files:**
- Update: GitHub repository slug, About description, and local `origin` URL.

- [x] Review the complete diff and stage only the approved design, plan, README, skill metadata, ignore rules, and showcase images.
- [x] Commit as `docs: make novel illustrator skill platform-neutral`.
- [x] Rename `NatBrian/epub-novel-illustrator` to `NatBrian/novel-illustrator`, update its description and `origin`, and push the current `main` branch.
- [x] Verify the remote URL and pushed commit.

### Task 4: Publish the repository

**Files:**
- Update: GitHub repository visibility.

- [x] Review tracked files and all committed history for credential-like values and generated EPUBs.
- [x] Set repository visibility to public.
- [x] Verify GitHub reports `PUBLIC` and the public `main` commit matches local `HEAD`.
