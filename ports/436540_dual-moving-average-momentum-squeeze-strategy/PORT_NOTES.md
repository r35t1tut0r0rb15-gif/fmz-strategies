# #436540 Dual Moving Average Momentum Squeeze Strategy -> `fmz_436540_squeeze_momentum_counter_candle`

- FMZ source id: 436540 (lineage).
- Source: https://www.fmz.com/strategy/436540 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-12-25 17:01:28). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C91). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Momentum sign and candle filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND436540. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length_kc` [20, 30] x `body_div` [3.0, 2.0]: **4 trials**; EMA 30 of the body fixed.

## Ambiguities resolved

- Squeeze flags are display only. REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator"`.

## Marks

`none`
