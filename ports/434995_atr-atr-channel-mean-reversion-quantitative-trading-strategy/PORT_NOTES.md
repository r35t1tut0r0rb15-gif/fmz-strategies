# #434995 基于ATR通道均线反转的量化交易策略ATR-Channel-Mean-Reversion-Quantitative-Trading-Strategy -> `fmz_434995_atr_open_stretch_long`

- FMZ source id: 434995 (lineage).
- Source: https://www.fmz.com/strategy/434995 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-11 15:38:25). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C72). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; exits on closes |
| 2 | PASS | ATR stretches from the open and an average |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The strategy() 100 % of equity, capital and commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`period` [10, 20] x `sl_mult` [1.5, 3.0]: **4 trials**.

## Ambiguities resolved

- Exits as close-based signals; the fill-bar stop test uses the old reference, as written. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion_band"`.

## Marks

`none`
