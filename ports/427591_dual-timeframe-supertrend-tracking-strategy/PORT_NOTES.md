# #427591 Dual-Timeframe Supertrend Tracking Strategy -> `fmz_427591_supertrend_flip_bracket`

- FMZ source id: 427591 (lineage).
- Source: https://www.fmz.com/strategy/427591 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-09-22 14:27:52). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C10). Not run.
- Near-duplicate group: **ND427591** (3 members, best partner #433448, Jaccard 0.705); ported anyway (rule 7).

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry. |
| 2 | ADAPT | 500 / 400 ticks -> ATR(14) multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND427591. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`factor` [1, 3] x `tp_atr` [0.3, 1] x `sl_atr` [0.25, 1]: **8 trials**; defaults 1 / 0.3 / 0.25; ATR period 1 fixed. 50 / 40 USD on 2-hour BTC bars is about 0.3 ATR (judgement before any backtest).

## Ambiguities resolved

- The "main" timeframe equals the chart's (2 hours): the filter is the trend itself.
- Stop module: `portfolio_kwargs` `{}`; REVERSAL INTENDED; stops on 2-hour bars: mark `coarse_bar_stop`. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`coarse_bar_stop`
