# #442834 基于双EMA价格摆动策略The-Dual-EMA-Price-Swing-Strategy -> `fmz_442834_hpotter_apo_sign_reversal`

- FMZ source id: 442834 (lineage).
- Source: https://www.fmz.com/strategy/442834 (PineScript v2, author ChaoZhang, FMZ last
  modified 2024-02-26 13:52:41). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C161). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA difference sign |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND427479. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`short_len` [10, 5] x `long_len` [20, 50]: **4 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
