# #439704 Golden Cross Death Cross Long term Multi factor Strategy -> `fmz_439704_sma10_50_golden_rsi_atr_bracket_long`

- FMZ source id: 439704 (lineage).
- Source: https://www.fmz.com/strategy/439704 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-23 11:11:40). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C123). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | PASS | SMA crossings, RSI and ATR distances |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The risk multiplier stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`risk_mult` [1.5, 3.0] x `slow` [50, 100]: **4 trials**; RSI 14 under 70 fixed.

## Ambiguities resolved

- Bracket from the signal close. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop`
