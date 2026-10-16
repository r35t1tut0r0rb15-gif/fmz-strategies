# #430176 Price Gap and Trend Following Trading Strategy -> `fmz_430176_brothejo_cci_rsi_ema200`

- FMZ source id: 430176 (lineage).
- Source: https://www.fmz.com/strategy/430176 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-10-25 18:02:11). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C33). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | CCI, RSI levels and standard-deviation bands. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND430176. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_period` [200, 100] x `band_mult` [1.6, 2.5]: **4 trials**; CCI 10 and RSI 14 / 35 / 65 fixed.

## Ambiguities resolved

- Both zero-cross tests are "either direction", as written. close_all wins over an entry when a position was held.
- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion_band"`.

## Marks

`none`
