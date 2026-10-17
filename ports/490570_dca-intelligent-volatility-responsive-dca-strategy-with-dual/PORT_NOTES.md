# #490570 智能波动跟踪型DCA策略与双轨止损系统-Intelligent-Volatility-Responsive-DCA-Strategy-with-Dual-Trailing-Stop-System -> `fmz_490570_ema_cross_dual_close_trail_long`

- FMZ source id: 490570 (lineage).
- Source: https://www.fmz.com/strategy/490570 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-04-14 18:18:25). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L2). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders and close-checked trails. |
| 2 | PASS | EMAs and percentages (the ATR-spaced adds are sizing). |
| 3 | PASS | 3Commas alert texts only. |
| 4 | DONE | Base and safety order sizes and the adds quoted, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG490570 (2 members, best partner #490797, Jaccard 0.910). |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`trail_pct` [8.0, 4.0] x `lock_in_trail_pct` [1.5, 3.0]: **4 trials**; defaults 8 / 1.5 (the source's); EMA 9 / 21,
the 2.5 % lock-in trigger and the 4-bar cooldown fixed.

## Ambiguities resolved

- Safety orders 1 / 2 are averaging in (criterion 4): not ported; the average entry is then the base fill.
- Both trails are close-checked exit signals (no mark), started on the first bar held.
- The commission is a cost, not in the module. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
