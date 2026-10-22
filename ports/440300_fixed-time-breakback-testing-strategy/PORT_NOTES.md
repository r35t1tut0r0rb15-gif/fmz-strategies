# #440300 Fixed Time Breakback Testing Strategy -> `fmz_440300_prev_candle_fade_tick_target`

- FMZ source id: 440300 (lineage).
- Source: https://www.fmz.com/strategy/440300 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-29 10:22:07). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C131). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; target fixed at entry |
| 2 | ADAPT | Tick targets -> ATR multiples |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`k_long` [0.67, 2.0] x `k_short` [0.33, 1.0]: **4 trials**; ATR 14 fixed.

## Ambiguities resolved

- Tick targets as ATR multiples; time test unused. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`
