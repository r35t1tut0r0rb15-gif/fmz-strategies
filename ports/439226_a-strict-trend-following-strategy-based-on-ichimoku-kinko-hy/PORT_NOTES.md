# #439226 A Strict Trend Following Strategy Based on Ichimoku Kinko Hyo -> `fmz_439226_badabing_ichimoku_alignment`

- FMZ source id: 439226 (lineage).
- Source: https://www.fmz.com/strategy/439226 (PineScript v3, author ChaoZhang, FMZ last
  modified 2024-01-18 15:03:28). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C118). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the per-bar stop pending |
| 2 | PASS | Ichimoku lines and ATR widths |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The fixed size stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`min_cloud_atr` [1.0, 0.5] x `atr_period` [20, 14]: **4 trials**; Ichimoku 9 / 26 / 52 / 26 fixed.

## Ambiguities resolved

- Per-bar span-A stop pending. Future cloud judged with the current ATR width, as written. REVERSAL INTENDED. FREQ = "30min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks

`trailing_stop_pending`
