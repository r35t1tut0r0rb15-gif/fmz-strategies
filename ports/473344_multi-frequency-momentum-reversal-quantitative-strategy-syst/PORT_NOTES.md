# #473344 Multi Frequency Momentum Reversal Quantitative Strategy System Multi Frequency Momentum Reversal Quantitative Strategy System -> `fmz_473344_loss_streak8_hold7_long`

- FMZ source id: 473344 (lineage).
- Source: https://www.fmz.com/strategy/473344 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-29 14:47:54). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C216). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Losing-streak entries with a time exit |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`streak` [8, 5] x `hold` [7, 3]: **4 trials**; direction Long, doji threshold fixed.

## Ambiguities resolved

- The Short direction option not ported (default Long). FREQ = "2D" (blocks of 2 broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

`none`
