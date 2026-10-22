# #442014 Multi Timeframe RSI SRSI Trading Strategy -> `fmz_442014_rsi_srsi_regime_turn_weekly_filter_long`

- FMZ source id: 442014 (lineage).
- Source: https://www.fmz.com/strategy/442014 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-18 16:13:50). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C150). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; weekly values from completed weeks |
| 2 | PASS | RSI / stochastic-RSI regimes and turns |
| 3 | PASS | Exchange pair in the header and as the ticker input (read as the current instrument). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tr_dur` [8, 5] x `diff` [5, 10]: **4 trials**; the thresholds fixed.

## Ambiguities resolved

- Ticker input read as the current instrument; weekly close from completed broker weeks. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
