# #483026 智能双均线交叉风险管理交易系统-Intelligent-Dual-SMA-Crossover-Risk-Management-Trading-System -> `fmz_483026_sma9_21_cross_pct_bracket`

- FMZ source id: 483026 (lineage).
- Source: https://www.fmz.com/strategy/483026 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-21 09:56:11). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L23). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket from the signal bar. |
| 2 | PASS | Moving averages and percentage distances. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing in the source; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`risk_pct` [1.0, 2.0] x `slow` [21, 50]: **4 trials**; defaults 1 / 21 (the source's); SMA 9 fixed; target = 2 x stop.

## Ambiguities resolved

- The "risk percentage" is the stop distance; `riskAmount` is never used. Crosses alternate, so no re-placement.
- REVERSAL INTENDED. Stop module: `portfolio_kwargs` {} (D4). FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
