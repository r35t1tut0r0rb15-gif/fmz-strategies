# #441961 Doubly Confident Price Oscillation Quant Strategy -> `fmz_441961_reversal123_apo_combo`

- FMZ source id: 441961 (lineage).
- Source: https://www.fmz.com/strategy/441961 (PineScript v3, author ChaoZhang, FMZ last
  modified 2024-02-18 10:10:16). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C149). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Close pattern, stochastic and APO states |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND426888. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 9] x `long_ema` [20, 40]: **4 trials**; short EMA 10 fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "combo_123_reversal"`.

## Marks

`none`
