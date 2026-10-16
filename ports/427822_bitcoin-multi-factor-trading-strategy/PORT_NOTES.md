# #427822 Bitcoin Multi-factor Trading Strategy -> `fmz_427822_3kilos_tema_atr_trend`

- FMZ source id: 427822 (lineage).
- Source: https://www.fmz.com/strategy/427822 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-09-25 18:24:02). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C13). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket at entry (moving version pending). |
| 2 | PASS | MA lengths, ATR multiple, percentages. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity stored; bracket quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`short` [50, 25] x `tp_pct` [1, 2] x `sl_pct` [3, 1.5]: **8 trials**; defaults 50 / 1 / 3 (the source's); TEMA 100 / 350, ATR 550 x 3 and SMA 100 fixed.

## Trailing stop (mark `trailing_stop_pending`)

The exit is re-issued on every longC / shortC bar with that bar's close, so the levels move while the signal repeats. Not expressible in the house spec: the port keeps the fixed bracket from the fill (`sl_stop` 0.03, `tp_stop` 0.01).

## Ambiguities resolved

- Heikin Ashi close of the chart's bars = ohlc4. Date filter dropped.
- Stop module: `portfolio_kwargs` `{}`; REVERSAL INTENDED. FREQ = "10min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`trailing_stop_pending`
