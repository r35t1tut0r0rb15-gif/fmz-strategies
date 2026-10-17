# #430877 DAKELAX-XRPUSDT-波尔带回归均线策略DAKELAX-XRPUSDT-Bollinger-Band-Mean-Reversion-Strategy -> `fmz_430877_asymmetric_bb_fade_long`

- FMZ source id: 430877 (lineage).
- Source: https://www.fmz.com/strategy/430877 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-11-02 16:18:34). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C41). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; adds not ported |
| 2 | PASS | Bollinger bands |
| 3 | PASS | Binance:XRPUSDT in the title and the pair in the header only; the rule reads the chart's own closes. |
| 4 | DONE | 20 units per order stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 50] x `lower_mult` [2.2, 1.5]: **4 trials**; the upper band's 1.5 sd fixed.

## Ambiguities resolved

- Adds not ported; the first order opens the long, close_all exits. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`
