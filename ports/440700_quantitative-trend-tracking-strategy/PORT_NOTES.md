# #440700 Quantitative Trend Tracking Strategy -> `fmz_440700_bb_rsi_adx_macd_session_long`

- FMZ source id: 440700 (lineage).
- Source: https://www.fmz.com/strategy/440700 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-01 11:42:22). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C138). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry from signal-bar data |
| 2 | PASS | Bollinger dip, RSI, ADX, Heikin-Ashi and MACD |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`mult` [4.989, 3.0] x `rsi_comp` [39.2, 50.0]: **4 trials**; the other lengths fixed.

## Ambiguities resolved

- Bracket fixed from the signal bar; session on the UTC bar open. Long only. FREQ = "5h".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`coarse_bar_stop`
