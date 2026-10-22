# #442955 Bollinger Band Tracking Strategy -> `fmz_442955_wma_band_touch_reversal_trail`

- FMZ source id: 442955 (lineage).
- Source: https://www.fmz.com/strategy/442955 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-27 16:11:44). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C164). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; target fixed at entry, the trail a house trail (approximation stated) |
| 2 | ADAPT | Tick target -> ATR multiple; tick trail -> percent trail |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The contract size and per-contract commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 50] x `trail_pct` [0.0238, 0.01]: **4 trials**; the deviation and the target multiple fixed.

## Ambiguities resolved

- Tick target as an ATR multiple; tick trail as a percent trail. REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`trailing_stop, coarse_bar_stop`
