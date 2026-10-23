# #468326 52周高低位-平均成交量-成交量突破策略-52-Week-High-Low-Average-Volume-Volume-Breakout-Strategy -> `fmz_468326_near_52w_high_volume_rise_no_exit_long_only`

- FMZ source id: 468326 (lineage).
- Source: https://www.fmz.com/strategy/468326 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-09-26 15:47:03). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V32). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Near-high volume breakouts |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`pct_from_high` [10.0, 5.0] x `vol_mult` [1.5, 2.0]: **4 trials**; 260 bars, volume SMA 50, 3 % limit.

## Ambiguities resolved

- No exit: one long held to the end of the data. Volume = broker tick volume. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "breakout"`.

## Marks

`none`
