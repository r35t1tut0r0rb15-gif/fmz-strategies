# #446782 Modified Bollinger Bands Strategy -> `fmz_446782_lower_band_above_sma50_stochrsi_long`

- FMZ source id: 446782 (lineage).
- Source: https://www.fmz.com/strategy/446782 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-04-01 15:58:23). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C177). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Lower-band dips in an uptrend with a stochastic-RSI filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 50] x `oversold` [20.0, 10.0]: **4 trials**; the SMA 50 and the stochastic-RSI lengths fixed.

## Ambiguities resolved

- Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`
