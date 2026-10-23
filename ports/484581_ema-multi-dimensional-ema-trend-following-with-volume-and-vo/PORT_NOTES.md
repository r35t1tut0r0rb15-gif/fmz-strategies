# #484581 多维度EMA趋势追踪与成交量波动率确认策略-Multi-Dimensional-EMA-Trend-Following-with-Volume-and-Volatility-Confirmation-Strategy -> `fmz_484581_ema20_persistence_volume_atr_pct_state_reversal`

- FMZ source id: 484581 (lineage).
- Source: https://www.fmz.com/strategy/484581 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-03 09:59:19). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V43). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA trend persistence with volume and volatility filters |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Capital stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`lookback` [50, 100] x `atr_pct` [0.01, 0.02]: **4 trials**; EMA 20, ATR 14.

## Ambiguities resolved

- Entries are states. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_persistence"`.

## Marks

`none`
