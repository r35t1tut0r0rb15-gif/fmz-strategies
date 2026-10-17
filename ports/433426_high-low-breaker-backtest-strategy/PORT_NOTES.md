# #433426 High Low Breaker Backtest Strategy -> `fmz_433426_high_low_breaker_bracket`

- FMZ source id: 433426 (lineage).
- Source: https://www.fmz.com/strategy/433426 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-11-27 15:37:13). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C60). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; fixed-percent bracket |
| 2 | PASS | Channel breaks and percent exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The strategy() 100 % of equity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_pct` [0.0015, 0.005] x `tp_pct` [0.001, 0.005]: **4 trials**; candles back 50 and ignore 30 fixed.

## Ambiguities resolved

- Dead max / min updates dropped. REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "donchian_breakout"`.

## Marks

`none`
