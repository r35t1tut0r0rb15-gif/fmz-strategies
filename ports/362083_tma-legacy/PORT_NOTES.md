# #362083 TMA Legacy -> `fmz_362083_rsi14_hidden_divergence_pivot5_reversal`

- FMZ source id: 362083 (lineage).
- Source: https://www.fmz.com/strategy/362083 (PineScript v5, author ChaoZhang, FMZ last
  modified 2022-05-09 22:59:36). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V2). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Hidden RSI divergences at pivots |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_length` [14, 21] x `lb` [5, 3]: **4 trials**; range 5-60 bars.

## Ambiguities resolved

- Volume not used (the VWMA / VWAP menu choices are not selected). REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
