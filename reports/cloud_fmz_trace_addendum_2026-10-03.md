# Addendum to the FMZ trace: batch 1 recovered and pushed; a contract check

- Written 2026-10-03 (UTC) by cloud session `session_01C2LkNFFeiH55j4hjeecivG`. Read-only on branch `survey`.
- It supersedes the "never pushed" findings of `cloud_fmz_trace_2026-10-03.md`. That report stays as written:
  it was true when written.

## 1. Recovery: done

- Session 5E-cloud (`session_01JYky9GB9AcWMXmECV7RiXE`) was resumed on 2026-10-03.
- It reported that its container still held every file, so nothing was recreated.
- It pushed branch `survey`. Checked here with `git ls-remote origin refs/heads/survey`:
  `741c1510e8f8abed3892a7c2c2dad2d84008b690`.
- Commits on `survey` beyond `master` (`7853bb2`):
  - `0d603b4` (2026-10-03 15:13:46Z): all batch-1 work;
  - `741c151` (15:14:12Z): `SURVEY_SUMMARY.md`, plus two narrowed checker rules.
- Files: **545 added, 0 modified, 0 deleted.** The 5,806 originals are untouched. The added files are:
  - `ports/`: 24 files, 6 ports x 4 files;
  - `flagged/`: 506 files, 253 x 2;
  - `survey_tools/`: 7 files;
  - the README, summary, progress file, `.gitignore` and four CSVs.
- `SURVEY_SUMMARY.md` gives these overall counts, total 5,806:

  | Outcome | Files |
  |---|---:|
  | PORT_CANDIDATE | 3,747 |
  | REJECTED | 994 |
  | HELD_NEEDS_VOLUME | 548 |
  | FLAGGED_CRYPTO_ONLY | 253 |
  | DUPLICATE | 251 |
  | REJECTED_ON_READING | 7 |
  | PORTED | 6 |

## 2. Batch 1 checked against the house contract

The contract is the latest staged `strategy-authoring` skill, `batch5g_F_staged_strategy-authoring_SKILL_part5h_2026-10-01.md`.

| Contract rule | Batch 1 | Note |
|---|---|---|
| §2: `FAMILY: str` is required in every module (deflation groups; the driver refuses a run spec naming another family) | **Missing in all 6** | The interface summary sent to 5E-cloud on 2026-09-29 left `FAMILY` out, so this is a gap in the spec, not a session error |
| §7: a per-bar `sl_stop`/`tp_stop` Series is read by vbt at the entry FILL bar, **unlagged**; compute it from earlier bars, `(k*atr/close).shift(1)` | **`SURVEY_README.md` (lines ~105–106) states the opposite** ("the desktop must apply the same one-bar lag") | No batch-1 port uses `stops()`, so no port is affected yet. The README must be corrected before any port uses a stop Series. The driver's start check marks a moving stop `stop_timing_fail`. |
| §3: declare opposite-entry behaviour | Declared in all 6: three are long-only; 11604, 55839 and 119038 say "REVERSAL INTENDED" | Compliant |
| §3: prefer flat before reverse (swap booking on the first flat bar) | 11604, 55839 and 119038 reverse in one bar | A preference, not a refusal. These trials can carry swap that vbt's sizing never sees (§3). |
| §7: the short exact replay does not cover `max_hold_time` or one-bar reversals (`not_replayable`, blocked from promotion) | 119038 reverses on its close-evaluated stop | Matters only once a port uses broker stops with shorts |
| §1/§2: `portfolio_kwargs` holds no `price=`/`open=` and no costs | All return `{}` | Compliant |
| §5: broker-day daily bars | No batch-1 port uses daily bars (FREQ is 1h, or 15min for 103070) | Not applicable yet |

## 3. 5E-cloud's four open questions: what the project files already answer

1. **Volume in `raw_1m_df`.**
   - Not stated in the contract: §2 requires only open/high/low/close.
   - The corporate-actions register §0.9 says to "check session validity before trusting any volume-based signal"
     (HANDOFF ~5999). That suggests volume exists in the stored data, but it is **not verified** from here, because
     the loader code is on the desktop.
   - **A decision is owed**, after a desktop check of the loader's columns.
2. **Stop Series timing.** **Answered by contract §7:** vbt reads it unlagged at the fill bar, and the module must
   shift it itself. 5E-cloud's assumption is wrong. No decision is needed, only a correction.
3. **Criterion-4 split.**
   - Consistent with contract §2/§7: `stops()` takes only `sl_stop`, `tp_stop` and `max_hold_time`, so trailing
     stops cannot be ported as stops.
   - Consistent with part 5j §2 item 6: "a Pine close-based stop is converted as a close-based exit, never as
     `sl_stop`".
   - Contract §7 adds that time exits meant for FTMO with shorts should be explicit exit signals, not
     `max_hold_time`.
   - Needs the user's confirmation.
4. **Default FREQ "1h" when the source has none.** No rule exists. **A decision is owed.**

## 4. Scale

- At about 13 files per batch, the 3,747 candidates need roughly 290 batches.
- The cloud credits expire 2026-11-05.
- Reading in ascending-id order will cover only a small, non-random slice. Most of that slice is old FMZ-API bots;
  the PineScript block starts at id 356844.
- **A decision is owed** on which subset to port and in what neutral order, declared before reading. For example,
  a seeded random sample of a fixed size, drawn from the PORT_CANDIDATE rows.
