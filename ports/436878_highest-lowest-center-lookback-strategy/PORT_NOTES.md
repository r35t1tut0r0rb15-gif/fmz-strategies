# #436878 Highest Lowest Center Lookback Strategy -> `fmz_436878_range_center_atr_band_long`

- FMZ source id: 436878 (lineage).
- Source: https://www.fmz.com/strategy/436878 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-28 15:42:10). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C97). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Range centre with ATR bands |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`lookback` [200, 100] x `atr_mult` [1.5, 2.5]: **4 trials**; smoother 5, ATR 10 and the 3-bar price SMA fixed.

## Ambiguities resolved

- Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_channel_breakout"`.

## Marks

`none`
