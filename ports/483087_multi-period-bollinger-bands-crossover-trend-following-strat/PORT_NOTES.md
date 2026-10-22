# #483087 Multi Period Bollinger Bands Crossover Trend Following Strategy -> `fmz_483087_bb20_120_240_all_lower_buy_all_upper_exit_long`

- FMZ source id: 483087 (lineage).
- Source: https://www.fmz.com/strategy/483087 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-27 17:02:33). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C256). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Three Bollinger bands at once |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length1` [20, 10] x `mult` [2.0, 1.5]: **4 trials**; lengths 120 / 240, one multiplier for all three bands.

## Ambiguities resolved

- Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`
