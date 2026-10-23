# #458180 Advanced Fibonacci Retracement and Volume Weighted Price Action Trading Strategy -> `fmz_458180_pin_engulf_volume_every20_fib_short_1h_reversal`

- FMZ source id: 458180 (lineage).
- Source: https://www.fmz.com/strategy/458180 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-07-30 16:13:37). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V32). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Pin-bar / engulfing candles on high volume |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fib_len` [20, 40] x `vol_mult` [1.5, 2.0]: **4 trials**; volume SMA 20.

## Ambiguities resolved

- Level array not var (0 on 19 of 20 bars); bar_index counted from the data start. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "candlestick_pattern"`.

## Marks

`none`
