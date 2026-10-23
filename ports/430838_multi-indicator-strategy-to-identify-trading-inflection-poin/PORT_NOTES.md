# #430838 Multi indicator Strategy to Identify Trading Inflection Points in Quant Trading -> `fmz_430838_schaff_trend_cycle_10_90_cross_pct_bracket_reversal`

- FMZ source id: 430838 (lineage).
- Source: https://www.fmz.com/strategy/430838 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-02 14:09:34). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V11). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; percent bracket from the fill |
| 2 | PASS | Schaff trend cycle crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The commented strategy() (1.5 % of equity, slippage 2) stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`cycle_length` [10, 20] x `stop` [0.05, 0.03]: **4 trials**; STC 23 / 50, TP 10 %.

## Ambiguities resolved

- STC only (no volume). REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "oscillator_threshold"`.

## Marks

`none`
