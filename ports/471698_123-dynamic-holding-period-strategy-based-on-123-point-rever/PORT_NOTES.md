# #471698 基于123点位反转的动态持仓期策略-Dynamic-Holding-Period-Strategy-Based-on-123-Point-Reversal-Pattern -> `fmz_471698_123_lower_low_reversal_timed_or_sma200_exit_long`

- FMZ source id: 471698 (lineage).
- Source: https://www.fmz.com/strategy/471698 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-12 15:15:46). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C210). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Lower-low reversal set-ups with a timed exit |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`days_to_hold` [7, 3] x `ma_len` [200, 20]: **4 trials**.

## Ambiguities resolved

- Hold count from the last set-up. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "reversal_pattern"`.

## Marks

`none`
