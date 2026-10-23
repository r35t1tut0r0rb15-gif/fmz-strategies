# #489042 多指标协同EMA交叉量化策略-Multi-Indicator-Synergistic-EMA-Crossover-Quantitative-Strategy -> `fmz_489042_ema20_50_cross_ema200_rsi_atr_volume_1h_reversal`

- FMZ source id: 489042 (lineage).
- Source: https://www.fmz.com/strategy/489042 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-04-01 14:46:06). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V46). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA crossings in the EMA 200 trend with volatility and volume filters |
| 3 | PASS | Exchange pair in the header only (ETH/USDT named in the title). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [20, 12] x `slow` [50, 26]: **4 trials**; EMA 200, RSI 14, ATR 14, volume SMA 20.

## Ambiguities resolved

- No exit (always in the market). Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
