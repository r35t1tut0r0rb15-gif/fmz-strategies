# #434187 Momentum Breakout Moving Average Trading Strategy -> `fmz_434187_rsi14_21_atr_test`

- FMZ source id: 434187 (lineage).
- Source: https://www.fmz.com/strategy/434187 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-04 15:57:06). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C65). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI crosses (the price-versus-ATR test is ported as written) |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_fast` [14, 7] x `rsi_slow` [21, 42]: **4 trials**; ATR 14 x 1.5 fixed.

## Ambiguities resolved

- Price compared with an ATR as written (always above). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
