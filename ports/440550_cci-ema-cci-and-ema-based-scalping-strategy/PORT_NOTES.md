# #440550 基于CCI和EMA的短线震荡策略CCI-and-EMA-Based-Scalping-Strategy -> `fmz_440550_ema_stack_cci200`

- FMZ source id: 440550 (lineage).
- Source: https://www.fmz.com/strategy/440550 (PineScript v3, author ChaoZhang, FMZ last
  modified 2024-01-31 16:01:21). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C136). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA stack and CCI |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`cci_len` [200, 100] x `slow` [50, 100]: **4 trials**; EMA 10 / 21 fixed.

## Ambiguities resolved

- Commented-out tick exits not ported. REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
