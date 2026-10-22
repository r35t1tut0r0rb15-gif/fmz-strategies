# #474053 G通道与EMA趋势过滤交易系统-G-Channel-and-EMA-Trend-Filter-Trading-System -> `fmz_474053_g_channel100_state_ema200_counter_reversal`

- FMZ source id: 474053 (lineage).
- Source: https://www.fmz.com/strategy/474053 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-05 16:27:24). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C221). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | G-Channel state with a counter-trend EMA filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [100, 50] x `ema_len` [200, 100]: **4 trials**.

## Ambiguities resolved

- nz seeds of 0, as written. REVERSAL INTENDED.

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_channel_breakout"`.

## Marks

`none`
