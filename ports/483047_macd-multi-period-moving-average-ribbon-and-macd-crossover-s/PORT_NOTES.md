# #483047 多周期均线带及MACD交叉策略系统-Multi-Period-Moving-Average-Ribbon-and-MACD-Crossover-Strategy-System -> `fmz_483047_ema9_21_macd_joint_cross_long`

- FMZ source id: 483047 (lineage).
- Source: https://www.fmz.com/strategy/483047 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-21 10:51:25). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L22). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Moving averages and MACD. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing in the source. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ma1_len` [9, 12] x `ma2_len` [21, 26]: **4 trials**; defaults 9 / 21 (the source's); MACD 12 / 26 / 9 fixed.

## Ambiguities resolved

- Clock (C6): `time("D")` changes at 00:00 UTC on the author's Binance chart (as #491506); that bar's signals are
  dropped, as written.
- MA types EMA (defaults; no VWMA, so no volume). Long only: opposite entries cannot occur. No stops. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
