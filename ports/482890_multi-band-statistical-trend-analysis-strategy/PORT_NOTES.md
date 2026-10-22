# #482890 Multi Band Statistical Trend Analysis Strategy -> `fmz_482890_close_vs_q95_20_minus_sd_state_long`

- FMZ source id: 482890 (lineage).
- Source: https://www.fmz.com/strategy/482890 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-20 16:45:59). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C252). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Close against a rolling quantile less one standard deviation |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity and capital stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 50] x `upper_quantile` [0.95, 0.9]: **4 trials**; confirmation 1 / 1 bar.

## Ambiguities resolved

- The quantile index uses half-up rounding, as Pine's math.round. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_channel_breakout"`.

## Marks

`none`
