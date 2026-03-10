# Add Development Log Entry

Append an entry to `docs/DEVLOG.md` with today's date, inserted after the `## Log` heading (reverse-chronological order — newest first).

Content to log: $ARGUMENTS

Format:
```
### YYYY-MM-DD — [Brief Title]
**Issues:** #N, #M

[What was done, decisions made, any notable details]

---
```

Rules:
- DEVLOG.md is append-only — never delete or modify past entries
- Insert new entries directly after the `## Log` line, before existing entries
- Use `###` (h3) for entry headings, not `##`
- Always include related issue numbers
- End each entry with a `---` separator
