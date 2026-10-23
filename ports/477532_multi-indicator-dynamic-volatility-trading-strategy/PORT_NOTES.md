# #477532 Multi Indicator Dynamic Volatility Trading Strategy -> `fmz_477532_sma9_21_cross_volume_atr_filter_long_only`

- FMZ source id: 477532 (lineage).
- Source: https://www.fmz.com/strategy/477532 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-01-06 11:47:06). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V36). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMA crossings filtered by volume and volatility |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [9, 12] x `slow` [21, 30]: **4 trials**; volume x 1.5, ATR 14.

## Ambiguities resolved

- Filtered close (may leave longs open). Volume = broker tick volume. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
