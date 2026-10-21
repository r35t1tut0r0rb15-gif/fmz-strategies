# #438020 Multi Timeframe Trailing Stop Loss Strategy -> `fmz_438020_mtf_atr_trailing_agreement`

- FMZ source id: 438020 (lineage).
- Source: https://www.fmz.com/strategy/438020 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-08 11:24:24). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C107). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | ATR trailing levels on four bar sizes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_mult` [2.0, 3.0] x `atr_length` [14, 28]: **4 trials**; the 2 / 3 / 4-hour sizes fixed.

## Ambiguities resolved

- Lower-timeframe levels = the day's last bar of each size (broker-day counted). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_stop_cross"`.

## Marks

`none`
