# #478717 Liquidity Weighted Moving Average Momentum Crossover Strategy -> `fmz_478717_liquidity_sampled_close_ema50_100_cross_long_only`

- FMZ source id: 478717 (lineage).
- Source: https://www.fmz.com/strategy/478717 (PineScript v6, author ChaoZhang, FMZ last
  modified 2025-01-17 15:45:55). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V37). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA crossings of liquidity-sampled closes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Commission and slippage stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [50, 20] x `slow` [100, 50]: **4 trials**; boundary EMA / stdev 10.

## Ambiguities resolved

- Doji liquidity is na. Volume = broker tick volume. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "liquidity_ma"`.

## Marks

`none`
