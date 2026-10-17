# #434293 Dual Moving Average Breakthrough Strategy -> `fmz_434293_ema_macd_pump_bracket`

- FMZ source id: 434293 (lineage).
- Source: https://www.fmz.com/strategy/434293 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-12-05 10:46:05). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C66). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; fixed-percent bracket |
| 2 | PASS | Average and MACD crosses, a bar-range threshold and percent exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG434293, ND430776. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [12, 6] x `pump` [0.08, 0.04]: **4 trials**; EMA 26, MACD 12 / 26 / 9 and the 5 % / 40 % bracket fixed.

## Ambiguities resolved

- One bracket for the three entry ids (same levels); later triggers while long ignored. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop`
