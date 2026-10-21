# #437742 Adaptive Trading Strategy Based on Momentum Indicators -> `fmz_437742_squeeze_di_momentum`

- FMZ source id: 437742 (lineage).
- Source: https://www.fmz.com/strategy/437742 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-05 11:43:25). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C105). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Volatility channels, DI and a regression momentum |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 30] x `mult_kc` [1.5, 2.0]: **4 trials**; DI 14 fixed.

## Ambiguities resolved

- BB deviation uses the KC factor as coded; closes after entries. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_regime"`.

## Marks

`none`
