# #489324 EMA辅助极点反转交易策略-EMA-Assisted-Extreme-Point-Reversal-Trading-Strategy -> `fmz_489324_cci_cross_rsi_extreme_ema100`

- FMZ source id: 489324 (lineage).
- Source: https://www.fmz.com/strategy/489324 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-04-03 14:50:24). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L4). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Oscillators and an EMA |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_oversold` [35, 30] x `use_divergence` [True, False]: **4 trials**; defaults 35 / on (the source's); CCI 10,
RSI 14, overbought 65 and EMA 100 fixed.

## Ambiguities resolved

- `ta.cross` is a cross in either direction: both "up" and "down" signals use any CCI zero cross, as written.
- Always in after the first signal (no other exit). REVERSAL INTENDED.
- Three-day bars from broker days in fixed blocks counted from 1970-01-01 (decision owed), as #426509.

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator_turn"`.

## Marks

`none`
