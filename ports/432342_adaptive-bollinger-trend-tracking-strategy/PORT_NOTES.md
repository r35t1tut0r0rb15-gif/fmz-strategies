# #432342 Adaptive Bollinger Trend Tracking Strategy -> `fmz_432342_linreg_band_levels_trail`

- FMZ source id: 432342 (lineage).
- Source: https://www.fmz.com/strategy/432342 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-16 16:35:01). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C51). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; stop fixed at entry; the trail is a house trail (approximation stated) |
| 2 | ADAPT | Tick distances -> ATR multiples / a fraction |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Qty 10 stored; the exits quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [40, 20] x `sl_atr` [0.035, 1.0]: **4 trials**; 2 sd, the levels 1 / 0 and the trail fixed.

## Ambiguities resolved

- Tick exits as ATR multiples / fractions (stated). The short wins a two-signal bar. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion_band"`.

## Marks

`trailing_stop`
