# #435265 Dynamic Moving Average Dual Strategy -> `fmz_435265_dynamic_ma_momentum_slopes`

- FMZ source id: 435265 (lineage).
- Source: https://www.fmz.com/strategy/435265 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-13 16:37:05). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C76). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the last-minute value is known at the bar's end |
| 2 | ADAPT | Price-unit threshold -> fraction of the close |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size and pyramiding 2 stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`malen` [5, 10] x `vol_min` [2.5, 1.0] x `mt_frac` [0.0, 0.0005]: **8 trials**; momentum length 3 and the other settings fixed.

## Ambiguities resolved

- security() at 1 minute is read as a last-minute value; price-unit threshold as a fraction. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator"`.

## Marks

`none`
