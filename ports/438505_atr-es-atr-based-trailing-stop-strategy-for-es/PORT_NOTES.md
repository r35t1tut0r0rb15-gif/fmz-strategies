# #438505 基于ATR的ES尾随停止策略ATR-based-Trailing-Stop-Strategy-for-ES -> `fmz_438505_atr_trend_change_hl2`

- FMZ source id: 438505 (lineage).
- Source: https://www.fmz.com/strategy/438505 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-12 14:52:23). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C111). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | ATR trend line changes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`periods` [10, 20] x `multiplier` [3.0, 2.0]: **4 trials**; source hl2 fixed.

## Ambiguities resolved

- Trailing exits never arm. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`
