# #439240 双B智能追踪策略Dual-B-Intelligent-Tracking-Strategy -> `fmz_439240_noro_bollinger_ohlc4_colour_exit`

- FMZ source id: 439240 (lineage).
- Source: https://www.fmz.com/strategy/439240 (PineScript v3, author ChaoZhang, FMZ last
  modified 2024-01-18 15:41:20). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C118). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Bollinger bands, bar colours and bodies |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND433588. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 50] x `mult` [2.0, 1.5]: **4 trials**; body EMA 30 fixed.

## Ambiguities resolved

- Exit precedence as written; the final close_all leaves the bar flat. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`
