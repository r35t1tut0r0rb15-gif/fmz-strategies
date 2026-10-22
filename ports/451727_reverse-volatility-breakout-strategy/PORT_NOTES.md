# #451727 Reverse Volatility Breakout Strategy -> `fmz_451727_faded_bollinger_breakout_rsi_macd_reversal`

- FMZ source id: 451727 (lineage).
- Source: https://www.fmz.com/strategy/451727 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-05-17 15:18:53). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C187). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Faded band breakouts with RSI / MACD agreement |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`bb_len` [20, 50] x `bb_mult` [2.0, 2.5] x `rsi_len` [14, 7]: **8 trials**; the MACD lengths fixed.

## Ambiguities resolved

- Previous-bar crossing. REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`
