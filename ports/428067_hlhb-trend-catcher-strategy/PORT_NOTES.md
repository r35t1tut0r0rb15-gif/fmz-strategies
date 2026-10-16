# #428067 HLHB Trend Catcher Strategy -> `fmz_428067_hlhb_trend_catcher`

- FMZ source id: 428067 (lineage).
- Source: https://www.fmz.com/strategy/428067 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-09-28 11:44:04). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C16). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry. |
| 2 | ADAPT | 400 / 150 ticks -> ATR(14) multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity stored; bracket quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tp_atr` [0.04, 2] x `sl_atr` [0.015, 1] x `adx_min` [25, 20]: **8 trials**; defaults 0.04 / 0.015 / 25 (the source's ticks on daily BTC, judgement before any backtest); EMAs 5 / 10, RSI 10, ADX 14 fixed.

## Ambiguities resolved

- trail_points without trail_offset arms no trail (not ported). The Friday 16:00 close cannot fire on daily bars (not ported).
- ADX as written. Stop module: `portfolio_kwargs` `{}`; REVERSAL INTENDED. Daily stops: mark `coarse_bar_stop`. Broker-day bars; FREQ = "1D".

## Decision owed

The distances were written as FX pips; the intended size on other instruments is unknown.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop`
