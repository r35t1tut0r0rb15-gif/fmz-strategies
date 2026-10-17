# #434610 Moving Average Pullback Trading Strategy -> `fmz_434610_sma_pullback_rsi3_bracket`

- FMZ source id: 434610 (lineage).
- Source: https://www.fmz.com/strategy/434610 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-07 18:09:27). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C69). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; fixed-percent bracket |
| 2 | PASS | Averages, a short RSI and percent exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The strategy() 100 % of equity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG434610. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`long_len` [200, 100] x `sl_pct` [0.05, 0.10]: **4 trials**; SMA 10, RSI 3 < 30 and the 20 % target fixed.

## Ambiguities resolved

- Flat tracked through the bracket and the exit signal. Mark coarse_bar_stop. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_pullback"`.

## Marks

`coarse_bar_stop`
