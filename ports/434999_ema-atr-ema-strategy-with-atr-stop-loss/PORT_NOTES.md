# #434999 基于EMA和ATR止损的趋势跟踪策略EMA-Strategy-with-ATR-Stop-Loss -> `fmz_434999_ema_13_48_cross`

- FMZ source id: 434999 (lineage).
- Source: https://www.fmz.com/strategy/434999 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-11 16:00:09). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C72). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Average crosses |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [13, 7] x `slow` [48, 100]: **4 trials**.

## Ambiguities resolved

- Plotted-only stop levels dropped. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
