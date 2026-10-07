# #361567 Optimized-Trend-Tracker -> `fmz_361567_ott_var_cross`

- Source: https://www.fmz.com/strategy/361567 (PineScript v4, OTT by KivancOzbilgic/Anil Ozeksi
  with orders added; FMZ last modified 2022-05-07 01:30:12). Verbatim here as `original_source.md`.
  Read 2026-10-07 (worker A).
- Status: PORTED (batch A4). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Pine bar-close evaluation, next-open fills. |
| 2 | ADAPT (screen: REVIEW) | Percent band (1.4 % of the average) -> `band_atr` x ATR(14); the OTT offset keeps the source's half-band ratio. |
| 3 | PASS | Binance futures pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | Group `ND361567` (0.65-0.80): partner #433011 (Jaccard 0.71, "Multiple Moving Average Dynamic Trend Strategy"), ported separately when reached. |
| 7 | IGNORED | |

## Declared grid (criterion 5)

`length` [2, 5, 10] x `band_atr` [1, 2, 3] = **9 trials**.

## Ambiguities resolved

- `crossover(MAvg, OTT[2])` compares with the OTT value two bars back (the plot is shifted the
  same way); reproduced.
- Only the VAR average (the default of eight options) is ported.
- `FREQ = "1h"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`: a ratcheting volatility band that flips direction.

## Marks (2026-10-07)

`none`
