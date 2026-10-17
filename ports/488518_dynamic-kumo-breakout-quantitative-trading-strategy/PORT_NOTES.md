# #488518 动态云层突破量化交易策略-Dynamic-Kumo-Breakout-Quantitative-Trading-Strategy -> `fmz_488518_kumo_break_long_sma_cross_short`

- FMZ source id: 488518 (lineage).
- Source: https://www.fmz.com/strategy/488518 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-03-28 15:16:43). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L10). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Range midpoints and moving averages. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`len_kijun` [26, 39] x `len_senkou` [52, 78]: **4 trials**; defaults 26 / 52 (the source's); Tenkan 9 and SMA 14 / 28
fixed.

## Ambiguities resolved

- The Senkou spans are used undisplaced, as written; `exitCondition` is computed but never used (not ported).
- Long on the cloud breakout, short on the SMA death cross: REVERSAL INTENDED; both on one bar, the short (written
  last) wins. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks

`none`
