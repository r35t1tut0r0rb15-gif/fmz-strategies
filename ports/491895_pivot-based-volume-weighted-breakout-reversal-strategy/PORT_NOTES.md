# #491895 Pivot Based Volume Weighted Breakout Reversal Strategy -> `fmz_491895_swing_sr_breakout_rejection_volume_rolling_pct_exits_reversal`

- FMZ source id: 491895 (lineage).
- Source: https://www.fmz.com/strategy/491895 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-04-24 17:08:39). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V48). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; per-bar re-sent percent exits followed in the signals |
| 2 | PASS | Swing-level breakouts and rejections on volume |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`pivot_len` [10, 5] x `tp_pct` [3.0, 5.0]: **4 trials**; volume SMA 20 x 1.5, stop 2 %.

## Ambiguities resolved

- Rolling percent exits followed at the next open. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "breakout"`.

## Marks

`trailing_stop_pending`
