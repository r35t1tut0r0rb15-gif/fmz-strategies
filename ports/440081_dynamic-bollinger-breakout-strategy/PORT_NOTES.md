# #440081 Dynamic Bollinger Breakout Strategy -> `fmz_440081_deep_lower_band_dip_long`

- FMZ source id: 440081 (lineage).
- Source: https://www.fmz.com/strategy/440081 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-26 14:52:59). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C130). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | ADAPT | Price-unit band margins -> fractions of the close |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The equity-based quantity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`buy_frac` [0.00138, 0.005] x `exit_frac` [0.0112, 0.02]: **4 trials**; BB 20 x 2 and the 1.25 % close fixed.

## Ambiguities resolved

- Price-unit margins as fractions; the "stop" closes at a 1.25 % gain, as written. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`
