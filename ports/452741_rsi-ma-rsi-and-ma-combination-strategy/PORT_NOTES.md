# #452741 RSI与MA组合策略RSI-and-MA-Combination-Strategy -> `fmz_452741_rsi70_strength_ema12_26_uptrend_long`

- FMZ source id: 452741 (lineage).
- Source: https://www.fmz.com/strategy/452741 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-05-28 17:34:11). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C189). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI strength in an EMA uptrend |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ob` [70, 60] x `short_len` [12, 9] x `long_len` [26, 50]: **8 trials**.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
