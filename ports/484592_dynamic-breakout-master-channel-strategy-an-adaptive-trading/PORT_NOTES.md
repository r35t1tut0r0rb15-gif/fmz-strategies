# #484592 动态突破大师通道策略基于支撑阻力突破的自适应交易系统-Dynamic-Breakout-Master-Channel-Strategy-An-Adaptive-Trading-System-Based-on-Support-and-Resistance-Breakouts -> `fmz_484592_pivot_zone_breakout`

- FMZ source id: 484592 (lineage).
- Source: https://www.fmz.com/strategy/484592 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-03-03 10:33:02). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L14). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Pivot zones scaled by the rolling range. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`period` [10, 5] x `width_pct` [5, 3]: **4 trials**; defaults 10 / 5 (the source's); min strength 1, 6 zones,
lookback 290 and the 300-bar range fixed.

## Ambiguities resolved

- `ta.pivothigh` / `pivotlow` as #430850 (strict on both sides), known 10 bars after the pivot: no look-ahead. The
  zone build, touch count and sort run exactly as written, including the sort's quirk (`power[y]` takes `power[x]`
  but `power[x]` keeps its value while the zones swap).
- Breakouts count only while the close is inside no zone; both on one bar: the short (written last) wins. REVERSAL
  INTENDED. Daily bars are broker days; FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "support_resistance_breakout"`.

## Marks

`none`
