# #477553 Multi Moving Average Supertrend with Bollinger Breakout Trading Strategy -> `fmz_477553_supertrend_up_ema13_34_100_adx25_reversal`

- FMZ source id: 477553 (lineage).
- Source: https://www.fmz.com/strategy/477553 (PineScript v6, author ChaoZhang, FMZ last
  modified 2025-01-06 13:48:19). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C233). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SuperTrend, EMA and ADX filters with SuperTrend-line closes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`adx_level` [25, 20] x `factor` [3.0, 2.0]: **4 trials**; EMA 13 / 34 / 100, ATR 10, DMI 14.

## Ambiguities resolved

- The short entry needs the SuperTrend up-trend, as written. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`
