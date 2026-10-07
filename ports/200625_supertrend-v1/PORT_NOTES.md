# #200625 SuperTrend-V1 -> `fmz_200625_supertrend_reverse`

- Source: https://www.fmz.com/strategy/200625 (Python, author homily, FMZ last modified
  2020-04-23 00:12:49). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A2). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Already runs on completed bars only (`records[:-1]`, once per new bar). |
| 2 | PASS | ATR-factor bands. |
| 3 | PASS (screen: REVIEW) | OKCoin quarterly contract is the venue only. |
| 4 | DONE | `vol` lots (2x on shorts), +/-1 % marketable prices, position close -> `original_sizing.txt`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED | |

## Declared grid (criterion 5)

`factor` [2, 3, 4] x `pd` [7, 10, 14] = **9 trials**.

## Ambiguities resolved

- The source's loop reads index `x-1 = -1` (the last row) at x = 0; the port starts the
  recursion at the first bar instead. Only warm-up bars differ, and no signal is emitted before
  ATR exists.
- `FREQ = "15min"` from `GetRecords(PERIOD_M15)`.

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks (2026-10-07)

`none`
