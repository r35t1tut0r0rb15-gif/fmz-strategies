# #483050 基于多重K线形态的三重打击量化交易策略-Multi-Candlestick-Pattern-Based-Triple-Strike-Quantitative-Trading-Strategy -> `fmz_483050_three_line_strike_reversal_1d`

- FMZ source id: 483050 (lineage).
- Source: https://www.fmz.com/strategy/483050 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-27 17:12:20). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L22). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Candle colours and body sizes. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`use_engulfing` [False, True]: **2 trials**; default False (the source's); the 3-line-strike entries always on.

## Ambiguities resolved

- The engulfing entries (off by default) are the grid's variant.
- REVERSAL INTENDED (always in once started); no exits or stops. Broker days stamped with their first minute (as
  #430984). FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "candlestick"`.

## Marks

`none`
