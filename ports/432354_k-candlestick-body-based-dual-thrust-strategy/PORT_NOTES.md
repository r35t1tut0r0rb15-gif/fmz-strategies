# #432354 基于K线实体的多空策略Candlestick-Body-Based-Dual-Thrust-Strategy -> `fmz_432354_noro_colorbar_fade`

- FMZ source id: 432354 (lineage).
- Source: https://www.fmz.com/strategy/432354 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-11-16 17:14:48). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C52). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Candle colours, body size against its own average, profit sign |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`body_len` [30, 15] x `use_body` [True, False]: **4 trials**.

## Ambiguities resolved

- close_all after the entries leaves an in-profit bar flat. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`
