# #427383 MACD Trading Strategy with Adaptive ATR Stop Loss -> `fmz_427383_macd_bf_atr_stop`

- FMZ source id: 427383 (lineage).
- Source: https://www.fmz.com/strategy/427383 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-20 15:23:00). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C6). Not run.
- Near-duplicate group: **ND427304** (3 members, with #427304, Jaccard 0.676); ported anyway (rule 7).

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; stop fixed at the signal. |
| 2 | PASS | MACD crosses, ATR multiple. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity stored; stop via `stops()`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND427304. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [13, 8] x `slow` [30, 50] x `atr_mult` [1.25, 2.5]: **8 trials**; defaults 13 / 30 / 1.25 (the source's); signal 12, ATR period 2 fixed.

## Ambiguities resolved

- Stop distance from the signal bar, re-based on the fill; the crosses alternate, so no stale-level re-entry.
- Broker-day bars; daily stops: mark `coarse_bar_stop`. Stop module: `portfolio_kwargs` `{}`; REVERSAL INTENDED. FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_momentum"`.

## Marks

`coarse_bar_stop`
