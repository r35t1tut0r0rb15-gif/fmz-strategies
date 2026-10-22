# #453267 EMA与布林带突破策略-EMA-and-Bollinger-Bands-Breakout-Strategy -> `fmz_453267_ema5_bollinger_trigger_bar_break_reversal`

- FMZ source id: 453267 (lineage).
- Source: https://www.fmz.com/strategy/453267 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-06-03 16:23:06). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C192). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the exit tests are bar-close tests |
| 2 | PASS | Trigger-bar breakdowns beyond the EMA and bands |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`bb_mult` [1.5, 2.0] x `ema_len` [5, 10] x `tgt_frac` [0.0238, 0.01]: **8 trials**; the band length 20 fixed.

## Ambiguities resolved

- Flag and position followed separately; target 1000 / 42000. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`
