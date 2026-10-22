# #454351 RSI低点反转策略-RSI-Low-Point-Reversal-Strategy -> `fmz_454351_rsi30_reentry_close_test_bracket_long`

- FMZ source id: 454351 (lineage).
- Source: https://www.fmz.com/strategy/454351 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-06-17 15:32:18). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C194). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the stop / target are close tests |
| 2 | PASS | RSI re-entries with close-test exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_len` [14, 7] x `sl_pct` [0.02, 0.05] x `tp_pct` [0.05, 0.10]: **8 trials**; the level 30 fixed.

## Ambiguities resolved

- Close tests against the latest signal close. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
