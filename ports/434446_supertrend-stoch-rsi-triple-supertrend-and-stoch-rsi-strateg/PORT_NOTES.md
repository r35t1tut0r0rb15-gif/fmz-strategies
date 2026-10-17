# #434446 三重SuperTrend和Stoch-RSI策略Triple-SuperTrend-and-Stoch-RSI-Strategy -> `fmz_434446_triple_supertrend_stoch_rsi`

- FMZ source id: 434446 (lineage).
- Source: https://www.fmz.com/strategy/434446 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-06 14:29:00). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C67). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket from the signal bar |
| 2 | PASS | Supertrends, a stochastic RSI and ATR exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The fixed quantity 10 stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_len` [200, 100] x `tp_mult` [1.6, 3.0]: **4 trials**; the Supertrends, the stochastic RSI and the 2.7 ATR stop fixed.

## Ambiguities resolved

- Script tracker ported as the entry gate; bracket from the signal close re-based on the fill. Mark coarse_bar_stop. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`coarse_bar_stop`
