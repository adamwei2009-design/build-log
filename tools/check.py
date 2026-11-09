#!/usr/bin/env python3
"""Upload safety check: run on any file or folder before it goes public (GitHub, LinkedIn, Reddit).

Usage:  python3 check.py <file-or-folder> [...]
Exit code 1 = problems found, do NOT upload.

Private words (company name, people's names) live in a local file, private-words.txt,
one per line. That file is never committed (see .gitignore), so this script stays generic."""
import re, sys, pathlib

RULES = [
  # secrets
  ("secret: private key", r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
  ("secret: API key/token", r"\b(sk-[A-Za-z0-9_-]{16,}|ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|xox[abp]-[A-Za-z0-9-]{10,}|AIza[0-9A-Za-z_-]{30,}|key_[A-Za-z0-9]{20,})"),
  ("secret: Bearer token", r"Bearer\s+[A-Za-z0-9._-]{16,}"),
  ("secret: password/key assignment", r"(?i)(?<![a-z])(password|passwd|api[_-]?key|secret|token|webhook[_-]?key)\s*[:=]\s*['\"]?(?=[^\s'\"]*\d)[^\s'\"]{8,}"),
  # where things live (lets people attack them)
  ("host: our worker/endpoint", r"(?i)[a-z0-9-]+\.[a-z0-9-]+\.workers\.dev|hooks\.zapier\.com/\S+|127\.0\.0\.1:\d+|localhost:\d+"),
  ("id: Google sheet/doc", r"\b1[A-Za-z0-9_-]{40,}\b"),
  ("id: Zapier workflow", r"\b01a1[0-9a-f]{4}-[0-9a-f]{4}-"),
  ("id: scheduled task", r"\btrig_[A-Za-z0-9]{10,}"),
  ("id: Cloudflare account", r"\b[0-9a-f]{32}\b"),
  ("path: PC folders", r"(?i)C:\\Users\\"),
  # company + people
  ("email address", r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[a-z]{2,}"),
  ("UK phone", r"(?<!\d)(0800\s?\d{3,4}\s?\d{3,4}|0\d{4}\s?\d{6}|07\d{3}\s?\d{6}|\+?44\s?7\d{3}\s?\d{6}|447\d{9})(?!\d)"),
  ("UK postcode", r"\b[A-Z]{1,2}\d[A-Z\d]?\s\d[A-Z]{2}\b"),
  ("job/customer ref", r"\b(CR|CB)-[A-Z0-9]{6}\b|\bjob\s?#?\d{5}\b"),
]
PRIVATE = pathlib.Path(__file__).with_name("private-words.txt")
if PRIVATE.exists():
    words = [w.strip() for w in PRIVATE.read_text().splitlines() if w.strip() and not w.startswith("#")]
    if words:
        RULES.append(("private word", r"(?i)\b(" + "|".join(map(re.escape, words)) + r")\b"))
ALLOW = {"noreply@anthropic.com", "users.noreply.github.com"}
TEXT = {".md",".txt",".html",".js",".ts",".py",".json",".csv",".yml",".yaml",".sh",""}

def files(paths):
    for p in map(pathlib.Path, paths):
        if p.is_dir():
            for f in p.rglob("*"):
                if f.is_file() and ".git" not in f.parts and f.name not in {"private-words.txt"} and f.resolve() != pathlib.Path(__file__).resolve() and f.suffix.lower() in TEXT: yield f
        elif p.is_file(): yield p

hits = 0
for f in files(sys.argv[1:]):
    for n, line in enumerate(f.read_text(errors="ignore").splitlines(), 1):
        for label, rx in RULES:
            for m in re.finditer(rx, line):
                if any(a in line for a in ALLOW) and label == "email address": continue
                hits += 1
                print(f"BLOCK  {f}:{n}  [{label}]  {m.group(0)[:60]}")
print(f"\n{'SAFE: 0 problems' if hits == 0 else f'NOT SAFE: {hits} problem(s). Fix before uploading.'}")
sys.exit(1 if hits else 0)
