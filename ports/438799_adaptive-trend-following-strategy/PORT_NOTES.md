# #438799 Adaptive Trend Following Strategy -> `fmz_438799_adaptive_trend_loss_cut`

- FMZ source id: 438799 (lineage).
- Source: https://www.fmz.com/strategy/438799 (PineScript v2, author ChaoZhang, FMZ last
  modified 2024-01-15 14:20:32). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C113). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-tested loss cut |
| 2 | PASS | Adaptive ATR trend line and entry-price tests |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`pd_` [2, 5] x `bw` [50, 25]: **4 trials**; factor limits 0.5 / 3 and BB 20 x 2 fixed.

## Ambiguities resolved

- Close-tested loss cut at the entry open; the script's flags followed. REVERSAL INTENDED. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`
