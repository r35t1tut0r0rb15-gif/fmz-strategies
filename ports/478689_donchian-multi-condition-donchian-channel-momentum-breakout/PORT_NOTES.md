# #478689 基于多重条件的Donchian通道动量突破策略-Multi-Condition-Donchian-Channel-Momentum-Breakout-Strategy -> `fmz_478689_lagged_donchian27_breakout_volume_mid_exit_long_only`

- FMZ source id: 478689 (lineage).
- Source: https://www.fmz.com/strategy/478689 (PineScript v6, author ChaoZhang, FMZ last
  modified 2025-01-17 14:28:22). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V37). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Lagged Donchian breakouts on volume, mid-channel exit |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity, capital and commission stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [27, 20] x `lag` [10, 0]: **4 trials**; volume x 1.4.

## Ambiguities resolved

- Channel lagged 10 bars. Volume = broker tick volume. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "channel_breakout"`.

## Marks

`none`
