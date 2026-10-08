# #427017 Dynamic Channel Breakout Strategy -> `fmz_427017_keltner_wick_long`

- Source: https://www.fmz.com/strategy/427017 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-09-16 22:46:42). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A29). Not run.

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

`kc_mult` [1.5, 2.0] x `tp_pct` [2.6, 1.3] x `sl_pct` [1.3, 0.65]: **8 trials**, defaults 1.5 / 2.6 / 1.3 (the source's); Keltner 14 fixed.

## Ambiguities resolved

- Static stop / target as fractions of the fill; simulate() mirrors them because entries need flat.
- Long only (shorts off by default); the multi-timeframe Keltner only plots.
- FREQ = "1min" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_channel_breakout"`.

## Marks (2026-10-07)

`none`
