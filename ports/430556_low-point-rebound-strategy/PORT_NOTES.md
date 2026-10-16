# #430556 Low Point Rebound Strategy -> `fmz_430556_five_bar_low_rsi2_long`

- FMZ source id: 430556 (lineage).
- Source: https://www.fmz.com/strategy/430556 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-10-30 11:53:56). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C36). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the time exit as a signal. |
| 2 | PASS | A price channel and an RSI level. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`low_len` [5, 10] x `time_stop` [5, 10]: **4 trials**; RSI 2 / 50 fixed.

## Ambiguities resolved

- Time exit as a signal (bars). Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
