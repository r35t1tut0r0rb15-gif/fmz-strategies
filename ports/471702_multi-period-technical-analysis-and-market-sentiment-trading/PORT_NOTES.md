# #471702 Multi Period Technical Analysis and Market Sentiment Trading Strategy -> `fmz_471702_sma10_30_cross_double_bottom_resistance_pattern_exit_long`

- FMZ source id: 471702 (lineage).
- Source: https://www.fmz.com/strategy/471702 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-12 15:52:16). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C210). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMA crossings and chart patterns with resistance exits |
| 3 | PASS | Exchange pair in the header only (XAUUSD named in the title). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`short_len` [10, 5] x `long_len` [30, 50]: **4 trials**; the pattern windows fixed.

## Ambiguities resolved

- Operator precedence as Pine; exact-equality patterns as written. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
