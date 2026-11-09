# Stage 4: what I found

Made-up data: 2,507 visits to homes over 2025 (repairs, services and installs). Every number here comes from stages 1 to 3 and is covered by a test.

## The short version

| # | Finding | So what |
|---|---|---|
| 1 | **Winter is the pressure point.** Repairs go from 48 a month in summer to 171 in December. Repair waits rise from 3.1 to 4.6 days, and the share waiting over 5 days goes from 15.3% to 37.6%. | Plan engineer time for November to February first. |
| 2 | **Services peak in October (112), just as repairs start climbing.** | Booking more services in the summer, when repairs are at their lowest, would free up winter time. |
| 3 | **14.8% of repairs need a second visit** (167 extra trips for 1,132 repairs). | Track first-time fix every month. It is the cheapest capacity there is. |
| 4 | **Areas earn about the same per job** (£406 to £436). West earns most in total only because it has the most jobs. | No action needed. |
| 5 | **One engineer is flagged as worse. The flag is wrong.** See below. | Treat a flag as a reason to look at the jobs, never as a verdict on a person. |

## The twist: my test flagged the wrong engineer

Stage 3 showed first-time fix rates from 73.9% to 91.9%. To see if any gap was real, I tested each engineer against everyone else (a two-proportion z-test). Because 12 tests at once will usually find *something* by luck, I used a Bonferroni correction.

One engineer was flagged: **ENG-08, 82 of 111 repairs fixed first time (73.9%), adjusted p = 0.004.**

But I made this data, so I know the truth. When I wrote the generator, I set:

- ENG-04 to fix **71%** first time (the one who really is worse)
- ENG-09 to fix 93%
- everyone else, ENG-08 included, to fix **86%**

So this year, the test pointed at someone who is average, and missed the one who really is worse (ENG-04 came out at 81.3%, close to normal).

Was the method broken, or was this year unlucky? I re-made the year 500 times with different random seeds and ran the same test on each one ([check_engineers.py](check_engineers.py)):

| Over 500 made-up years | Times | Share |
|---|---|---|
| The right engineer (ENG-04) was flagged | 411 | 82% |
| A wrong engineer was flagged | 15 | 3% |

The method works most of the time. This year happens to be one of the rare bad draws.

**What I take from it:**

- With around 100 jobs each, even a correct method gets it wrong sometimes.
- In real data you never get to see the answer key. So a flag should start a conversation (what kind of jobs did they get? older boilers? harder areas?), not end one.
- Never name a person from one number.

## What this analysis can't tell you

- The data is made up. The method is the point, not the numbers.
- One year only, so no trend from year to year.
- Waits are in calendar days, not working days.
- There's no fault type or boiler age, so a hard mix of jobs can't be told apart from a weaker engineer. That's exactly what caught out finding 5.

## Files

- [check_engineers.py](check_engineers.py): the z-test, the correction and the 500-year check
- [check_engineers_output.txt](check_engineers_output.txt): its full output
