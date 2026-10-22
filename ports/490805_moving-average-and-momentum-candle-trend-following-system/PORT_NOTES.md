# #490805 Moving Average and Momentum Candle Trend Following System -> `fmz_490805_momentum_candle_sma200_side_pip_bracket_flat`

- FMZ source id: 490805 (lineage).
- Source: https://www.fmz.com/strategy/490805 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-04-16 16:01:57). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C273). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; pip bracket as fractions of the fill |
| 2 | ADAPT | Pip distances read as percents at the header price |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | 10 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_pct` [2.5, 5.0] x `maLength` [200, 100]: **4 trials** (target 2 x the stop); pips at TRX 0.2.

## Ambiguities resolved

- Pips read at TRX 0.2. Entries only from flat (a loop follows the bracket). FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "candlestick_pattern"`.

## Marks

`coarse_bar_stop`
