# #474982 Dynamic Dual Supertrend Volume Price Strategy -> `fmz_474982_supertrend_cross_volume_atr_bracket_reversal`

- FMZ source id: 474982 (lineage).
- Source: https://www.fmz.com/strategy/474982 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-13 11:54:44). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V35). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; ATR bracket at the signal close as fractions of the fill |
| 2 | PASS | Supertrend crossings on high volume |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`factor` [3.0, 2.0] x `vol_mult` [1.5, 2.0]: **4 trials**; ATR 10; SL 1.5, TP 3 ATR.

## Ambiguities resolved

- Bracket at the signal close. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`coarse_bar_stop`
