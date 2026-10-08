# #426500 AO Moving Average AO Indicator Trading Strategy -> `fmz_426500_ma_ao_long`

- Source: https://www.fmz.com/strategy/426500 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-12 16:09:01). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A22). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar-derived quantities only. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast_ma` [8, 13] x `slow_ma` [20, 34]: **4 trials**, defaults 8 / 20 (the source's); AO 5 / 8 fixed.

## Ambiguities resolved

- Long only.
- |AO| == 1 means dif rising; with dif na the comparison is false (|AO| == 2), as Pine.
- FREQ = "30min" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator_turn"`.

## Marks (2026-10-07)

`none`
