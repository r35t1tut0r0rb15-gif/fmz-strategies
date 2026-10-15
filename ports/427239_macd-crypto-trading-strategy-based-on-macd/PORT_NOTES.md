# #427239 Crypto Trading Strategy Based on MACD -> `fmz_427239_ema_direction_bracket`

- FMZ source id: 427239 (lineage).
- Source: https://www.fmz.com/strategy/427239 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-09-19 11:21:42). Verbatim here as `original_source.md`. Read 2026-10-15 (FMZ-C).
- Status: PORTED (batch C3). Not run.
- Near-duplicate group: **ND427239** (with #428795, Jaccard 0.732); ported anyway (rule 7).

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry. |
| 2 | ADAPT | 1,500 / 20,000 ticks -> `sl_atr` / `tp_atr` x ATR(14). |
| 3 | PASS | "Crypto" in the name only. |
| 4 | DONE | Bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND427239. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_atr` [4, 2] x `tp_atr` [50, 10] x `slow` [26, 50]: **8 trials**; defaults 4 / 50 / 26; fast EMA 12 fixed. On the source's 10-minute BTC bars 1,500 ticks (150 USD) is about 3-5 ATR and 20,000 ticks about 40-60 ATR (judgement, stated before any backtest).

## Ambiguities resolved

- MACD / RSI extremes only colour bars.
- trail_points without trail_offset places no trailing stop: none ported.
- Backtest date window dropped. Stop module: `portfolio_kwargs` `{}`; one-bar reversals (REVERSAL INTENDED).
- FREQ = "10min" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_momentum"`.

## Marks

`none`
