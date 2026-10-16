# #427512 RSI Long Term Trading Strategy -> `fmz_427512_body_momentum_daily`

- FMZ source id: 427512 (lineage).
- Source: https://www.fmz.com/strategy/427512 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-09-21 20:54:08). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C9). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | ADAPT | 5-digit point thresholds (x 100000) -> ATR(14) multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity stored; the risk rule is commented out. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`up_sum_atr` [0.5, 1] x `down_sum_atr` [0.3, 0.6] x `atr_length` [14, 28]: **8 trials**; defaults 0.5 / 0.3 / 14; small body 0.05 ATR, down move 0.6 ATR, RSI floor 30.1 fixed. Conversion: 350 / 35 / 200 / 400 points against a daily EUR/USD ATR of about 70 pips (judgement before any backtest).

## Ambiguities resolved

- The x 100000 point scaling is FX-specific: thresholds in ATR instead.
- REVERSAL INTENDED (no other exit). Broker-day bars. FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`
