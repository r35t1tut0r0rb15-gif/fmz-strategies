# #473318 基于EMA均线波动带的多周期趋势跟踪交易系统-Multi-Period-Trend-Following-Trading-System-Based-on-EMA-Volatility-Bands -> `fmz_473318_ema300_2sd_band_reentry_reversal_limit_pending`

- FMZ source id: 473318 (lineage).
- Source: https://www.fmz.com/strategy/473318 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-29 10:49:30). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C216). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA band re-entries; per-bar limit described (pending) |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent limit stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [300, 150] x `mult` [2.0, 2.5]: **4 trials**; the per-bar limit pending.

## Ambiguities resolved

- Per-bar limit pending (trailing_stop_pending). REVERSAL INTENDED.

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`trailing_stop_pending`
