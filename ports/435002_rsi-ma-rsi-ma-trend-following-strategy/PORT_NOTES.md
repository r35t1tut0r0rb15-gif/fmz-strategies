# #435002 基于RSI指标和MA均线的趋势跟踪策略RSI-MA-Trend-Following-Strategy -> `fmz_435002_rsi4_extreme_tick_bracket`

- FMZ source id: 435002 (lineage).
- Source: https://www.fmz.com/strategy/435002 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-12-11 16:14:07). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C72). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | ADAPT | Tick distances -> ATR multiples |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code; the bracket quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsin` [5, 15] x `atr_scale` [1.0, 10.0]: **4 trials**; `atr_scale` multiplies both ATR distances (0.075 / 0.115); RSI 4 and ATR 14 fixed.

## Ambiguities resolved

- Tick bracket -> ATR multiples. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
