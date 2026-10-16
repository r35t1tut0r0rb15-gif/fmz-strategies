# #430271 RSI多空动量策略RSI-Momentum-Long-Short-Strategy -> `fmz_430271_connors_rsi2_long_short`

- FMZ source id: 430271 (lineage).
- Source: https://www.fmz.com/strategy/430271 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-10-26 17:05:40). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C34). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | RSI levels and moving averages. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`over_sold` [10, 5] x `ma_long` [200, 100]: **4 trials**; over-bought = 100 - over-sold; RSI 2 and SMA 5 fixed.

## Ambiguities resolved

- The script's entry state equals the position (no stops). REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
