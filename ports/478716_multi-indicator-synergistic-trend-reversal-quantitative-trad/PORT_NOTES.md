# #478716 Multi Indicator Synergistic Trend Reversal Quantitative Trading Strategy -> `fmz_478716_extreme_close_reversal_volume_atr_bracket_reversal`

- FMZ source id: 478716 (lineage).
- Source: https://www.fmz.com/strategy/478716 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-01-17 15:44:01). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V37). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; ATR bracket at the signal close as fractions of the fill |
| 2 | PASS | Contrarian extreme-close reversals on volume |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`lookback` [12, 8] x `rr` [2.0, 1.5]: **4 trials**; volume SMA 20, ATR 14 x 1.5.

## Ambiguities resolved

- Repeated signals re-send the bracket (pending). Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "reversal_extreme"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
