# #488545 Market Structure Swing Trading Strategy -> `fmz_488545_choch_bos_rsi_volume_atr_bracket_reversal`

- FMZ source id: 488545 (lineage).
- Source: https://www.fmz.com/strategy/488545 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-28 17:38:45). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V45). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; ATR bracket at the signal close as fractions of the fill |
| 2 | PASS | Change-of-character structure breaks with RSI and volume filters |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 5 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`swing_len` [50, 20] x `rsi_os` [30.0, 40.0]: **4 trials**; RSI 14, volume x 1.2, ATR 14 x 2 / 3.

## Ambiguities resolved

- RSI filters oppose the breakout direction, as written. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "market_structure"`.

## Marks

`coarse_bar_stop`
