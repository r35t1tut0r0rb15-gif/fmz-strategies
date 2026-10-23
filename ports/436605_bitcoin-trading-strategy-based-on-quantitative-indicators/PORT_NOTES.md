# #436605 Bitcoin Trading Strategy Based on Quantitative Indicators -> `fmz_436605_hull180_qqe_mod_volume_osc_swing_bracket_reversal`

- FMZ source id: 436605 (lineage).
- Source: https://www.fmz.com/strategy/436605 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-26 11:06:12). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V19). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; swing-distance bracket from the fill |
| 2 | PASS | Hull trend with QQE-mod and volume-oscillator confirmation |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Qty = 0.5 fixed, slippage 25, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`hull_len` [180, 100] x `rr` [1.5, 2.0]: **4 trials**; QQE 6 / 5 / 3, BB 50 x 0.35, swing 7.

## Ambiguities resolved

- RsiMa2 = RsiMa (same inputs). Bracket as fractions of the fill. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "qqe"`.

## Marks

`none`
