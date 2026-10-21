# #436781 快速EMA和慢速EMA动量突破策略fast-EMA-and-slow-EMA-Momentum-Breakthrough-Strategy -> `fmz_436781_ema_37_370_cross_long_only`

- FMZ source id: 436781 (lineage).
- Source: https://www.fmz.com/strategy/436781 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-27 16:35:04). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C96). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA crossing |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [37, 20] x `slow` [370, 200]: **4 trials**.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
