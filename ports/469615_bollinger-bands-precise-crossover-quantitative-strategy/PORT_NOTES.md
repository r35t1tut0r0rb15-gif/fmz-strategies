# #469615 Bollinger Bands Precise Crossover Quantitative Strategy -> `fmz_469615_outside_band_candle_recovery_reversal`

- FMZ source id: 469615 (lineage).
- Source: https://www.fmz.com/strategy/469615 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-10-14 11:38:31). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C208). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Outside-band candle recoveries |
| 3 | PASS | Exchange pair in the header only (BTCUSDT named in the title). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 50] x `multiplier` [1.2, 2.0]: **4 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`
