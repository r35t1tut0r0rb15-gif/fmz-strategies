# #446525 超级趋势ATR策略Supertrend-ATR-Strategy -> `fmz_446525_supertrend10x3_flip_atr_bracket_reversal`

- FMZ source id: 446525 (lineage).
- Source: https://www.fmz.com/strategy/446525 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-03-29 11:29:15). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C175). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed on the signal bar |
| 2 | PASS | SuperTrend flips with an ATR bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The 1 % risk quantity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`multiplier` [3.0, 2.0] x `sl_mult` [1.5, 3.0]: **4 trials**; the ATR periods and the 1 : 1 ratio fixed.

## Ambiguities resolved

- Levels fixed per trade. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`
