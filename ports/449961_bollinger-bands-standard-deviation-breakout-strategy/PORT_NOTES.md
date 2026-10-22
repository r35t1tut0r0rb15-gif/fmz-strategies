# #449961 Bollinger-Bands-Standard-Deviation-Breakout-Strategy-布林带标准差突破策略 -> `fmz_449961_one_sd_band_breakout_basis_exit_reversal`

- FMZ source id: 449961 (lineage).
- Source: https://www.fmz.com/strategy/449961 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-04-30 16:51:34). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C182). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | One-sd band breakouts with basis exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 50] x `k` [1.0, 2.0]: **4 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_breakout"`.

## Marks

`none`
