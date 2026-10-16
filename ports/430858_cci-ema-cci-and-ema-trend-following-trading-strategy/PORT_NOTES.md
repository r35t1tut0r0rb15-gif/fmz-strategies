# #430858 基于CCI和EMA的趋势跟随交易策略CCI-and-EMA-Trend-Following-Trading-Strategy -> `fmz_430858_cci_ema_sign`

- FMZ source id: 430858 (lineage).
- Source: https://www.fmz.com/strategy/430858 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-02 15:17:22). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C40). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | The sign of a smoothed CCI. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity per entry stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 40] x `length_cci_ema` [12, 24]: **4 trials**; buy / sell points 0 fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator_turn"`.

## Marks

`none`
