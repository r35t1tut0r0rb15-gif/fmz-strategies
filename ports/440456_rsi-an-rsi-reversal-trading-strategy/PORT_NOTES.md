# #440456 基于RSI指标的反转交易策略An-RSI-Reversal-Trading-Strategy -> `fmz_440456_rsi_alternating_liquidation_exits`

- FMZ source id: 440456 (lineage).
- Source: https://www.fmz.com/strategy/440456 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-30 17:06:45). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C135). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bar-tested levels |
| 2 | ADAPT | Price-unit levels -> fractions |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code (leverage sets the liquidation level only). |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND431415. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`level_frac` [0.0238, 0.5] x `length` [14, 7]: **4 trials**; the same fraction for trail, target and stop; leverage 200 fixed.

## Ambiguities resolved

- Price amounts as fractions; liquidation level from the signal open. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
