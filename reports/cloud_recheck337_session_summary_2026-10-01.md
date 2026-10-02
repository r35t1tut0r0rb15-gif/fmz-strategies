# Cloud session summary: the 337 re-check (2026-10-01)

Claude Code cloud session on `r35t1tut0r0rb15-gif/fmz-strategies`, branch `claude/peaceful-turing-keqi5r`. This is the
end-of-session summary given to the user in chat, saved so the project chat and later sessions have it. The full
report is `cloud_recheck337_2026-10-01.md` in this folder.

## What "337" was
The 337 "probable" rows of cloud batch 5f: coarse-bar (over 60 minutes) FMZ strategies whose stop was found by keyword
only and flagged "needs a manual check before use". The project's open question **Y14 (c)** (stops on daily bars are
charged the expensive rollover cost) was waiting on this count, so the re-check was needed, not obsolete.

## What was found
- **The key distinction:** only a stop that fills *inside* the bar gets the wrong cost. A stop written as "if the close
  is below the stop, exit" fills at the next bar's open, where the rollover cost is correct.
- **The 337 split three ways:** 16 affected (all read by hand); 226 have a real stop that fills at the next bar's open
  (not affected); 95 have no working stop at all (stop variables only plotted, never used, or meaning something else,
  e.g. `TP` = typical price).
- **Y14 (c) population, revised:** about **1,030 coarse-bar strategies** (1,031 files; 692 daily) have a stop that
  fills inside the bar, not the 1,352 batch 5f estimated.
- **New problem:** 32 strategies attach their stop-loss/take-profit to the *entry* order in Pine, which makes the entry
  a stop order and gives no stop exit. How to convert these is a decision owed.
- **5G-A owed 3:** about 7 in 10 stop strategies can reverse (893 of 1,248 Pine files); time-based exits are rare
  (24 likely, 33 possible). If the exact re-check is extended, reversals should come first, the opposite of the 5G-A
  report's suggestion.
- **Accuracy:** 179 of the 337 hand-checked, including every row that affects the count. In random spot-checks of
  the rest, 2 of 20 were wrong; both were false "stops" that do not change the count of 16.
- **Caveat:** still the original FMZ source code, not converted strategies. Q1 (where the conversion output went) is
  unanswered.

## Where it is
- **Drive, this folder** (`Claude handoff/reports/cloud_recheck337_2026-10-01/`): the report (with "For the project
  chat": four decisions and recommendations), `cloud_recheck337_2026-10-01_no-filenames.csv`,
  `cloud_owed3_flags_2026-10-01.md`, and this summary. Each was checked byte for byte against the repository copy. An
  earlier copy of the report, uploaded before a last fix, is renamed `..._SUPERSEDED_2026-10-01T2015Z.md` (nothing went
  to the Drive trash).
- **GitHub:** branch `claude/peaceful-turing-keqi5r`, folder `reports/`: the full tables with file names and the
  scripts that reproduce everything. No pull request was opened.

## Saving to Drive from cloud sessions
Desktop sessions save automatically because they write into the synced `G:\My Drive` folder. Cloud sessions have no
synced folder, so this session uploaded each file through the Google Drive connector, into the same folder layout as
the earlier cloud sessions. The user's personal preferences do reach cloud sessions, so adding this line to them would
make every cloud session do it without being asked:

> In Claude Code cloud sessions, upload every report, log and results file to Google Drive
> `Claude handoff/reports/cloud_<task>_<date>/` as you produce them, and never use the Drive trash.

## Next
No need to switch chat or model yet. The obvious next step, the minute-data stop fix for Y14 (c), needs the data on the
desktop, so it is a job for a desktop session rather than this cloud one.
