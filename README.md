# Build log

![tests](https://github.com/adamwei2009-design/build-log/actions/workflows/tests.yml/badge.svg)

Things I've built during my Data Technician apprenticeship, one write-up per build.
All examples use made-up data. No real customer details, company names or keys are in this repo.

**Start here if you're hiring a data analyst:** the [service jobs analysis](analysis/service-jobs/). Cleaning, SQL, charts and findings on a made-up dataset, with 23 tests that check the numbers add up.

How I work: I design the process, set the rules and test it. AI helps me write the code. Nothing goes live until it has passed a test with fake data, and every build has an undo.

| # | Build | Status | What I learned |
|---|---|---|---|
| 1 | [Enquiry auto-reply](builds/01-enquiry-auto-reply.md) | Live | An automation isn't finished until you can prove it didn't miss anything |
| 2 | [WhatsApp quote journey](builds/02-whatsapp-quote-journey.md) | Live | Measure each step before blaming the tool |
| 3 | [Automatic warranty emails](builds/03-warranty-emails.md) | Live | Automate the send, keep a "needs a person" list |
| 4 | Duplicate lead checker (Cloudflare) | Testing | Only act on your own when you're certain |
| 5 | [The automation that watches my automation](builds/05-watchdog.md) | Live | Automations fail quietly, so build the alarm too |
| tool | [Upload safety check](tools/) | In use | Check before you publish, every time |
| data | [Service jobs analysis: a data journey](analysis/service-jobs/) | Done (4 stages) | A test can flag the wrong person, so check before you blame |
| report | [The monthly review that adds up](builds/monthly-review.md) | Live | Before you make a report look nice, check it adds up |
| code | [Working examples with tests](examples/) | 10 tests passing | Merge repeat alerts, route by context, safe deletes, clean images |

More coming each week.
