# #428000 Triple EMA Momentum Strategy -> `fmz_428000_triple_dema_session_scalper`

- FMZ source id: 428000 (lineage).
- Source: https://www.fmz.com/strategy/428000 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-27 17:19:26). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C15). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry. |
| 2 | ADAPT | 50 / 100 ticks -> ATR(14) multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Risk-based size stored; bracket quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tp_atr` [0.1, 1] x `sl_atr` [0.2, 2] x `len1` [25, 15]: **8 trials**; defaults 0.1 / 0.2 / 25; DEMAs 50 / 100 and the window fixed. 5 / 10 USD on 15-minute BTC is about 0.1 / 0.2 ATR (judgement before any backtest).

## Ambiguities resolved

- Sessions in the exchange's time (UTC on Binance): both on, so 03:00-16:00 UTC by bar open time (session-open line in the docstring).
- Stop module: `portfolio_kwargs` `{}`; REVERSAL INTENDED. FREQ = "15min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
