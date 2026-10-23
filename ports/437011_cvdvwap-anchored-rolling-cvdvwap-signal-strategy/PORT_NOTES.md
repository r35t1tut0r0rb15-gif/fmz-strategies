# #437011 基于锚定滚动CVDVWAP的信号策略Anchored-Rolling-CVDVWAP-Signal-Strategy -> `fmz_437011_roc7_burst_cvd_anchored_vwap_swing_bracket_reversal`

- FMZ source id: 437011 (lineage).
- Source: https://www.fmz.com/strategy/437011 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-29 14:56:03). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V19). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; swing stop and distance target as fractions of the fill |
| 2 | PASS | Momentum bursts with volume and anchored-VWAP filters |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`move_pct` [8.0, 5.0] x `sl_periods` [200, 50]: **4 trials**; analysis 7, anchor 20, CVD 20, TP 200 %.

## Ambiguities resolved

- Target from the previous trade's entry price, as written; wrong-side targets dropped. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "vwap_breakout"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
