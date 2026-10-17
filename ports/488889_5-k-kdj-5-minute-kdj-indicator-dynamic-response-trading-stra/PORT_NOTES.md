# #488889 5分钟K线KDJ指标动态响应交易策略-5-Minute-KDJ-Indicator-Dynamic-Response-Trading-Strategy -> `fmz_488889_fast_stoch_k_extremes`

- FMZ source id: 488889 (lineage).
- Source: https://www.fmz.com/strategy/488889 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-03-31 16:26:56). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L8). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | An oscillator only |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The full-equity quantity quoted (slippage is a cost). |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [5, 14] x `entry_band` [5, 15]: **4 trials**; defaults 5 / 5 (the source's: long below 5, short above
100 - 5 = 95); the 90 / 10 exits fixed.

## Ambiguities resolved

- Source order long entry, long close, short entry, short close; closes act on the position held at the bar's start.
- REVERSAL INTENDED. Broker-day bars; FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "stochastic_oscillator"`.

## Marks

`none`
