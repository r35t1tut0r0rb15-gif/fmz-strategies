# #430678 Bollinger Band Momentum Burst Strategy -> `fmz_430678_bb_expansion_4h_trend`

- FMZ source id: 430678 (lineage).
- Source: https://www.fmz.com/strategy/430678 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-31 15:54:41). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C38). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-checked exits; completed higher-timeframe values. |
| 2 | ADAPT | The 3-decimal rounding of the levels dropped. |
| 3 | PASS | "EURUSD" in the title only; exchange pair in the header. |
| 4 | DONE | The risk-rule options quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_multi` [3.0, 2.0] x `rr` [1.5, 2.0]: **4 trials**; BB 40 / 20 / 2, valid length 14, EMA 14 / 3 on 4 hours fixed.

## Ambiguities resolved

- 4-hour values from completed blocks. ATR levels from the fill bar's close, close-checked. Rounding dropped.
- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_squeeze"`.

## Marks

`none`
