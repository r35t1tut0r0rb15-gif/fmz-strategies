# #474846 Multi Technical Indicator Based Trend Following and Momentum Strategy -> `fmz_474846_ema200_macd_rsi50_70_state_long`

- FMZ source id: 474846 (lineage).
- Source: https://www.fmz.com/strategy/474846 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-12 15:01:09). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C225). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Trend / momentum states |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Percent-of-equity size stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_length` [200, 100] x `rsi_length` [14, 7]: **4 trials**; MACD fixed.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`
