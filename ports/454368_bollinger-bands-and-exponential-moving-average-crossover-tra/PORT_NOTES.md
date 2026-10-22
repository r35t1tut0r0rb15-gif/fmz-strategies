# #454368 Bollinger Bands and Exponential Moving Average Crossover Trading Strategy -> `fmz_454368_open_beyond_band_close_back_ema5_reversal`

- FMZ source id: 454368 (lineage).
- Source: https://www.fmz.com/strategy/454368 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-06-17 16:58:43). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C195). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Band-open reversal bars with an EMA 5 close |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 50] x `mult` [2.0, 2.5] x `ema_len` [5, 9]: **8 trials**.

## Ambiguities resolved

- The flag blocks never act. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`
