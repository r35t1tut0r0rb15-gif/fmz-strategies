# #451706 RSI与MACD结合的多空策略-RSI-and-MACD-Combined-Long-Short-Strategy -> `fmz_451706_rsi_reentry_macd_cross_exit_reversal`

- FMZ source id: 451706 (lineage).
- Source: https://www.fmz.com/strategy/451706 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-05-17 11:04:03). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C186). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI re-entries with MACD exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_len` [14, 7] x `ob` [70, 80] x `os` [30, 20]: **8 trials**; the MACD lengths fixed.

## Ambiguities resolved

- Call order. REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
