# #361966 Buy Sell Strat -> `fmz_361966_ema9_21_cross_volume_surge_four_close_pattern_reversal`

- FMZ source id: 361966 (lineage).
- Source: https://www.fmz.com/strategy/361966 (PineScript v5, author ChaoZhang, FMZ last
  modified 2022-05-09 11:24:33). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V1). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA crossings with volume and pattern confirmation |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG361966. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`vol_factor` [0.85, 0.6] x `slow` [21, 50]: **4 trials**; EMA 9, volume window 5.

## Ambiguities resolved

- Volume = broker tick volume. REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
