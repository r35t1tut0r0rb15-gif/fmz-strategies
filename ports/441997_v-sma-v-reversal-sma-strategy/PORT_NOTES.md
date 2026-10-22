# #441997 基于V型反转指标SMA策略V-Reversal-SMA-Strategy -> `fmz_441997_smoothed_vortex_cross_reversal`

- FMZ source id: 441997 (lineage).
- Source: https://www.fmz.com/strategy/441997 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-18 15:04:34). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C149). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Smoothed vortex crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`period` [14, 21] x `smooth_len` [14, 7]: **4 trials**.

## Ambiguities resolved

- One entry per direction (default pyramiding). REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "directional_movement"`.

## Marks

`none`
