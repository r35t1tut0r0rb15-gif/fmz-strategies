# #432880 Heikin-Ashi-HighLow通道动态均线交易策略Heikin-Ashi-HighLow-Channel-Dynamic-Moving-Average-Trading-Strategy -> `fmz_432880_heikin_ashi_hilo_channel_long`

- FMZ source id: 432880 (lineage).
- Source: https://www.fmz.com/strategy/432880 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-22 14:43:58). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C54). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Heikin Ashi channel |
| 3 | PASS |  |
| 4 | DONE | 100 % of equity stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`len_h` [5, 10] x `len_l` [5, 10]: **4 trials**.

## Ambiguities resolved

- No bar size: FREQ = "bar_size_pending", bars from bar_sizes.build_bars. Long only.

## FAMILY (proposed, user to confirm)

`FAMILY = "heikin_ashi_trend"`.

## Marks

`bar_size_pending`
