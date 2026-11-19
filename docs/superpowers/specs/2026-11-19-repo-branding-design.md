# Repository branding refresh

## Intent

Make this reusable EPUB illustration skill easy to understand and install from both Codex and Antigravity. The README will show real, labeled examples, and Git will stop presenting timestamped production runs as source files.

## Approaches

1. Keep the current repository slug and clarify cross-platform support in the README.
2. Rename the GitHub repository and the skill metadata to `novel-illustrator`, then update the README and ignore rules. **Selected** because it is concise and independent of any one agent.
3. Use a CLI-focused name such as `epub-illustration-toolkit`.

## Scope and constraints

- Rename the GitHub repo to `novel-illustrator`; keep the local checkout directory unchanged.
- Update the GitHub About description to identify Codex and Antigravity support.
- Align the `SKILL.md` front matter name and README references with the new slug.
- Rewrite README installation instructions for Codex and Antigravity using their current user and workspace skill paths.
- Add two unchanged Chapter 1 illustrations under `docs/showcase/`, captioned with the novel and chapter, with descriptive alt text.
- Remove blanket PNG and JPG ignores so the showcase images can be committed. Ignore timestamped production folders, work data, and EPUB outputs.
- Keep the README professional and free of em dashes.
- Do not modify the Python tools, illustration outputs, or skill workflow itself.
- Make the repository public after checking tracked files and commit history for sensitive content.

## Completion

Commit the README, skill name, ignore rules, showcase assets, and this short design record, then rename the GitHub repository, update its About description and `origin`, push the requested branch, and make the repository public after the history review. If GitHub reports the chosen slug is unavailable, pause before using an alternate public name.
