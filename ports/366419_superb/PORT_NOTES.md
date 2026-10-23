# #366419 SuperB -> `fmz_366419_volume_spread_shadow_ema10_atr_band_pct_reversal_tracker`

- FMZ source id: 366419 (lineage).
- Source: https://www.fmz.com/strategy/366419 (PineScript v4, author Zer3192, FMZ last
  modified 2022-05-29 10:40:45). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V3). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Volume-price shadow line with a percent reversal tracker |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG366419. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`len` [10, 20] x `factor` [0.05, 0.02]: **4 trials**; ATR 10 x 1, windows 28 / 14.

## Ambiguities resolved

- Zero-range bars add 0 to the running sum. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "atr_trailing_line"`.

## Marks

`none`
