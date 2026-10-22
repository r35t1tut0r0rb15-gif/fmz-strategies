# #440373 Robust Trend Continuation Strategy -> `fmz_440373_ema50_pullback_continuation_atr`

- FMZ source id: 440373 (lineage).
- Source: https://www.fmz.com/strategy/440373 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-29 16:57:01). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C133). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; stop fixed at entry from signal-bar data |
| 2 | PASS | EMA pullback and ATR levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_factor` [3.5, 2.0] x `tp_factor` [3.5, 2.0]: **4 trials**; EMA 50 / 80 / 200 and ATR 14 fixed.

## Ambiguities resolved

- Signal-bar ATR; stop held from the fill. Long only. FREQ = "10min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_pullback"`.

## Marks

`none`
