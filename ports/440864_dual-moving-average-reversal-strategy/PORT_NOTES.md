# #440864 Dual Moving Average Reversal Strategy -> `fmz_440864_sma14_28_state_long_stop_trail`

- FMZ source id: 440864 (lineage).
- Source: https://www.fmz.com/strategy/440864 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-02 17:37:16). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C141). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the trail is a house trail (approximation stated) |
| 2 | PASS | SMA state |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Capital, percent-of-capital orders and commission settings. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`stop_loss` [0.02, 0.05] x `trail_trigger` [0.012, 0.03]: **4 trials**; trail distance 0.253 and SMA 14 / 28 fixed.

## Ambiguities resolved

- Trailing take profit as a house trail (approximation); Long Only default. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`trailing_stop, coarse_bar_stop`
