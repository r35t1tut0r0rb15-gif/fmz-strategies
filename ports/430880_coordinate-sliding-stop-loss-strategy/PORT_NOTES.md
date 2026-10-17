# #430880 Coordinate Sliding Stop Loss Strategy -> `fmz_430880_stoch_rsi_roc_bracket`

- FMZ source id: 430880 (lineage).
- Source: https://www.fmz.com/strategy/430880 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-02 16:28:55). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C41). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; fixed percentage bracket |
| 2 | PASS | Stochastic RSI, ROC and percentage stops |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND430880. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`roc_len` [14, 28] x `sl_pct` [2.0, 4.0]: **4 trials**; RSI 5, stoch 7, D 7, ROC threshold 2 and TP 9 % fixed.

## Ambiguities resolved

- Bracket from the fill bar (the source starts it one bar later). Mark coarse_bar_stop. REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "stochastic_oscillator"`.

## Marks

`coarse_bar_stop`
