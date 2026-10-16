# #427304 Center of Gravity SSL Channel Trend Following Strategy -> `fmz_427304_cog_ssl_roc`

- FMZ source id: 427304 (lineage).
- Source: https://www.fmz.com/strategy/427304 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-19 21:30:23). Verbatim here as `original_source.md`. Read 2026-10-15 (FMZ-C).
- Status: PORTED (batch C5). Not run.
- Near-duplicate group: **ND427304** (3 members, best partner #429390, Jaccard 0.697); ported anyway (rule 7).

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; stop fixed at the signal. |
| 2 | ADAPT | CoG band +-6 % of close -> `cog_atr` x ATR(14); ROC % kept (a return). |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity, commission stored; stop via `stops()`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND427304. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`cog_atr` [4, 2] x `pcnt_change` [10, 4] x `atr_mult` [2, 3]: **8 trials**; defaults 4 / 10 / 2; SSL 12 / 13, linreg 25 / 5, ROC 2, ATR stop period 1 fixed. 6 % of a 1-hour BTC close is several ATRs (judgement, stated before any backtest).

## Ambiguities resolved

- **Stated deviation:** Pine keeps the first long signal's stop LEVEL when the strategy re-enters after a stop-out without an opposite signal; the port re-bases the 2 x ATR(1) distance on each fill.
- Entries are emitted on every bar the condition holds (Pine re-enters after a stop-out). Both conditions on one bar: the side opposite the last signalled side.
- Stop module: `portfolio_kwargs` `{}` (driver D4); REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`
