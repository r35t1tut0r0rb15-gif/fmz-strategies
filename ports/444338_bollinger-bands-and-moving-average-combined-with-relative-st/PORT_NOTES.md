# #444338 Bollinger Bands and Moving Average Combined with Relative Strength Index Trading Strategy -> `fmz_444338_band_ema3_rsi_cross_reversal`

- FMZ source id: 444338 (lineage).
- Source: https://www.fmz.com/strategy/444338 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-03-11 11:02:44). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C170). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Band, EMA and RSI crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 50] x `rsi_length` [14, 7]: **4 trials**; the multiplier, the EMA 3 and the RSI levels fixed.

## Ambiguities resolved

- No exit, as written. REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`
