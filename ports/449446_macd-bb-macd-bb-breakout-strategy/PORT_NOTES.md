# #449446 MACD-BB-波段突破策略-MACD-BB-Breakout-Strategy -> `fmz_449446_macd_own_band_breakout_reversal`

- FMZ source id: 449446 (lineage).
- Source: https://www.fmz.com/strategy/449446 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-04-25 17:16:28). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C179). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | MACD band breakouts |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [10, 20] x `dev` [1.0, 2.0]: **4 trials**; the MACD lengths fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_momentum"`.

## Marks

`none`
