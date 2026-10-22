# #441103 Trend Following Stop Loss Strategy Based on Trend Alert Indicator -> `fmz_441103_always_long_structure_stop_bracket`

- FMZ source id: 441103 (lineage).
- Source: https://www.fmz.com/strategy/441103 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-05 16:00:35). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C146). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry from signal-bar data |
| 2 | PASS | Structure stop and half-distance target |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The alert risk input stored (not an order size). |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`lookback` [8, 20] x `limit_mult` [0.5, 1.0]: **4 trials**; ATR 15 x 0.2 fixed.

## Ambiguities resolved

- TrendAlert = close is always positive: long only, re-entered from flat. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "atr_trailing_line"`.

## Marks

`coarse_bar_stop`
