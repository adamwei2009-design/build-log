# Upload safety check

A small Python script I run on every file before it goes public, so nothing private leaks by accident.

**It blocks:** private keys, API keys and tokens, passwords in config, webhook and worker URLs, local server addresses, long document and workflow IDs, Windows user paths, email addresses, UK phone numbers, UK postcodes, job references, and any private words you list (company name, people's names).

```bash
python3 check.py my-post.md builds/
# SAFE: 0 problems          -> ok to upload
# NOT SAFE: 3 problem(s)    -> exit code 1, fix first
```

Put private words in `private-words.txt` next to the script, one per line. That file is in `.gitignore`, so it's never published.

**How I tested it:** a test file with 7 planted problems (a phone number, an email, a worker URL, a postcode, a name, a company name, a token). It caught all 7. Then I ran it on everything already published: 0 problems.

Built with AI help. I set what it must catch and tested it.
