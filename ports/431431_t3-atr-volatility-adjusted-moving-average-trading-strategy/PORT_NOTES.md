# #431431 基于T3移动平均线和ATR的交易策略Volatility-Adjusted-Moving-Average-Trading-Strategy -> `fmz_431431_ut_bot_t3_bracket`

- FMZ source id: 431431 (lineage).
- Source: https://www.fmz.com/strategy/431431 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-11-07 17:18:05). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C46). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; levels fixed at entry (rule 2) |
| 2 | PASS | ATR trailing line, a T3 filter and ATR brackets |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Qty 1 in the alert text only; no sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG431431. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`key` [1.0, 2.0] x `t3_len` [100, 50]: **4 trials**; ATR 50 and R:R 1 fixed.

## Ambiguities resolved

- Pending (not emitted as written): levels moved by a new setup during a position. Mark coarse_bar_stop.
  REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_stop_cross"`.

## Marks

`trailing_stop_pending, coarse_bar_stop`
