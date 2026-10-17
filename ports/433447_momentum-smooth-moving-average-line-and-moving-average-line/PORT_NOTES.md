# #433447 Momentum Smooth Moving Average Line and Moving Average Line Crossover Strategy -> `fmz_433447_alma_ema_cross_bracket`

- FMZ source id: 433447 (lineage).
- Source: https://www.fmz.com/strategy/433447 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-11-27 17:35:09). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C60). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; fixed-percent bracket |
| 2 | PASS | Average crosses, an ALMA filter and oscillator levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code; the bracket quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`slow` [49, 30] x `alma_len` [130, 65]: **4 trials**; EMA 9, the ALMA offset / sigma, stoch RSI and the bracket fixed.

## Ambiguities resolved

- Long on the slow EMA crossing above the fast one, as written; same-bar cancels honoured. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop`
