# #489280 市场结构突破与成交量峰值RSI多重指标交叉策略-Market-Structure-Breakthrough-with-Volume-Spike-and-RSI-Confluence-Strategy -> `fmz_489280_swing_level_cross_volume_spike_rsi_3bar_hold_1h`

- FMZ source id: 489280 (lineage).
- Source: https://www.fmz.com/strategy/489280 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-04-03 10:23:22). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V46). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; a 3-bar time exit in the signals |
| 2 | PASS | Swing-level crossings on volume spikes with an RSI filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Initial capital only (no sizing). |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`hold` [3, 6] x `vol_mult` [2.0, 1.5]: **4 trials**; pivots 5 / 5, volume SMA 20, RSI 14 at 50.

## Ambiguities resolved

- Long on a cross above the swing low, short below the swing high, as written. Volume = broker tick volume. Flat-only entries. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "breakout"`.

## Marks

`none`
