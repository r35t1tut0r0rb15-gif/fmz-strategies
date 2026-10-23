# #483502 Multi Dimensional Technical Indicator Fusion Trend Breakthrough Strategy -> `fmz_483502_pattern_finder_shoulders_double_tops_volume_atr_1h_reversal`

- FMZ source id: 483502 (lineage).
- Source: https://www.fmz.com/strategy/483502 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-27 16:51:34). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V42). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; ATR bracket at the signal close as fractions of the fill |
| 2 | PASS | Chart-pattern approximations on volume |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_mult` [1.5, 2.5] x `vol_mult` [1.2, 1.5]: **4 trials**; EMA 50, ATR 14, patterns 20 / 30 / 50.

## Ambiguities resolved

- Left-shoulder shorts dominate; breakouts never fire. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "chart_pattern"`.

## Marks

`trailing_stop_pending`
