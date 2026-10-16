# #428692 Dual Moving Average Breakout Strategy -> `fmz_428692_two_ema_pairs_tick_bracket`

- FMZ source id: 428692 (lineage).
- Source: https://www.fmz.com/strategy/428692 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-10-08 13:59:27). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C18). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry. |
| 2 | ADAPT | 6250 / 3500 ticks -> ATR(14) multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Cash quantity stored; bracket quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tp_atr` [3, 6] x `sl_atr` [1.75, 3.5]: **4 trials**; defaults 3 / 1.75 (about 625 / 350 USD on hourly BTC, judgement before any backtest); EMAs 59 / 82 / 96 / 95 fixed.

## Ambiguities resolved

- qty_percent 100 = full exit. A same-bar long and short cross: the long (first order) is kept.
- Stop module: `portfolio_kwargs` `{}`; REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
