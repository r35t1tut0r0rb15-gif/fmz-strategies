# #471672 均线修正型RSI三重验证机会策略-Triple-Validated-RSI-Mean-Reversion-with-Moving-Average-Filter-Strategy -> `fmz_471672_connors_rsi2_three_day_slide_long`

- FMZ source id: 471672 (lineage).
- Source: https://www.fmz.com/strategy/471672 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-12 11:37:20). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C209). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI 2 slides in an uptrend |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`entry_th` [10, 20] x `exit_th` [70, 50] x `sma_len` [200, 100]: **8 trials**; the 60 start fixed.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
