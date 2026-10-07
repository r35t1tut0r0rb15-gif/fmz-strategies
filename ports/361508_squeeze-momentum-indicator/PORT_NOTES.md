# #361508 Squeeze-Momentum-Indicator -> `fmz_361508_squeeze_momentum_turn`

- Source: https://www.fmz.com/strategy/361508 (PineScript, LazyBear's SQZMOM with orders added;
  FMZ last modified 2022-05-08 11:17:04). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A4). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Pine bar-close evaluation, next-open fills. |
| 2 | PASS | Only the sign and direction of the histogram are used. |
| 3 | PASS | Bitfinex spot pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | One parameter drives the orders; see grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED | |

## Declared grid (criterion 5)

`length_kc` [10, 14, 20, 30] = **4 trials**. The BB length/multipliers only colour the plot.

## Ambiguities resolved

- The BB deviation uses `multKC` (LazyBear's known slip); it does not affect the orders.
- Counter-momentum: a falling positive histogram goes short, a rising negative one goes long.
- `FREQ = "1D"` broker days from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator_turn"`: trades turns of a momentum histogram.

## Marks (2026-10-07)

`none`
