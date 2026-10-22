# #443643 连续K线反转突破策略Consecutive-Candlestick-Reversal-Breakout-Strategy -> `fmz_443643_down_run_rebound_close_stop_long`

- FMZ source id: 443643 (lineage).
- Source: https://www.fmz.com/strategy/443643 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-03-05 16:07:40). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C168). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Close-run reversal with close-tested exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG443643. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`bars_up` [2, 3] x `bars_down` [3, 5]: **4 trials**; the ATR settings fixed.

## Ambiguities resolved

- The active flag as written (signal-bar exits act on nothing). Long only. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "reversal_pattern"`.

## Marks

`none`
