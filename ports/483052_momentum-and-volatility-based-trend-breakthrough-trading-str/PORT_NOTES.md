# #483052 基于动量与波动率的趋势突破交易策略-Momentum-and-Volatility-Based-Trend-Breakthrough-Trading-Strategy -> `fmz_483052_percent_b_cmo_joint_cross_1d`

- FMZ source id: 483052 (lineage).
- Source: https://www.fmz.com/strategy/483052 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-27 17:09:24). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L22). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bollinger %B and CMO. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing in the source. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`bb_mult` [2.0, 2.5] x `cmo_len` [14, 9]: **4 trials**; defaults 2 / 14 (the source's); BB 20 fixed.

## Ambiguities resolved

- `ta.cmo` as Pine defines it; `ta.stdev` is the population standard deviation.
- REVERSAL INTENDED (always in once started); no exits or stops. Broker days stamped with their first minute (as
  #430984). FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "oscillator_cross"`.

## Marks

`none`
