# #440877 Price Divergence Based Trend Trading Strategy -> `fmz_440877_macd_hist_fractal_divergence_murrey_osc_2h_reversal`

- FMZ source id: 440877 (lineage).
- Source: https://www.fmz.com/strategy/440877 (PineScript v2, author ChaoZhang, FMZ last
  modified 2024-02-02 18:00:55). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V25). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | MACD-histogram fractal divergences confirmed by the Murrey math oscillator |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Strategy(): 10 % of equity, capital 10000, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [100, 50] x `quad` [2, 1]: **4 trials**; MACD 12 / 26 / 9 (SMA based).

## Ambiguities resolved

- The trailing exit never acts (no offset). Volume not used. REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_variant"`.

## Marks

`none`
