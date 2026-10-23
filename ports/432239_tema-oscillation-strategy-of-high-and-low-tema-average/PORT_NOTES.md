# #432239 高低TEMA平均值震荡策略Oscillation-Strategy-of-High-and-Low-TEMA-Average -> `fmz_432239_vwmacd_hma400_tema_short_pct_bracket`

- FMZ source id: 432239 (lineage).
- Source: https://www.fmz.com/strategy/432239 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-15 17:49:52). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V12). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket at the signal close as fractions of the fill |
| 2 | PASS | Volume-weighted MACD and TEMA trend shorts under a Hull MA |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Strategy(): 100 % of equity, commission 0.018 %, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`hma_len` [400, 200] x `tema_slow` [8, 13]: **4 trials**; VWMACD 13 / 21 / 5, TEMA fast 5, TP 1 %, SL 4 %.

## Ambiguities resolved

- Short only (the "BUY" id is a short). Bracket fixed at the signal close. Volume = broker tick volume. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_variant"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
