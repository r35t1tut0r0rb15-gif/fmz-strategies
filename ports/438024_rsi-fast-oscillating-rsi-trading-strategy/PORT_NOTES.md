# #438024 快速震荡RSI交易策略Fast-Oscillating-RSI-Trading-Strategy -> `fmz_438024_noro_frsi_red_bar_dip_long`

- FMZ source id: 438024 (lineage).
- Source: https://www.fmz.com/strategy/438024 (PineScript v3, author ChaoZhang, FMZ last
  modified 2024-01-08 11:50:38). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C108). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Fast RSI levels and bar bodies |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND432219. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`limit` [30, 20] x `dnrsiperiod` [9, 14]: **4 trials**; up period 2, RSI bars 1 and the body EMA 30 fixed.

## Ambiguities resolved

- Non-var sps has no effect; shorts not traded. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
