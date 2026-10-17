# #491506 双均线回调反转交易策略基于EMA穿越与回测容差的趋势跟踪系统-Dual-EMA-Retest-Reversal-Strategy-A-Trend-Following-System-Based-on-EMA-Crossovers-and-Retest-Tolerance -> `fmz_491506_ema_200_500_retest_bracket`

- FMZ source id: 491506 (lineage).
- Source: https://www.fmz.com/strategy/491506 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-04-21 15:58:18). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L1). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the re-placed bracket fixed at entry (mark). |
| 2 | PASS | EMAs and percentages. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 1 % of equity quoted; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`retest_tolerance` [0.002, 0.001] x `risk_reward` [4.0, 2.0]: **4 trials**; defaults 0.002 / 4 (the source's);
EMA 200 / 500, stop 0.5 % and two signals a day fixed.

## Re-placed bracket (rule 2, mark `trailing_stop_pending`)

The `strategy.exit` with the entry is re-issued on every counted retest bar, also while the trade is open (the
entry itself is then ignored), so a later retest moves the stop and target to that bar's close x (1 -+ 0.5 %) /
(1 +- 2 %). The port keeps the bracket of the entry (`sl_stop` 0.005, `tp_stop` 0.02 of the fill price).

## Ambiguities resolved

- The two-a-day counter counts every retest bar under the limit (as written, even when the entry is ignored) and
  resets at 00:00 UTC, the author's exchange day. Decision owed: keep UTC days or use broker days.
- A short retest while long reverses (the trend flips only on a cross). REVERSAL INTENDED. FREQ = "2min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_pullback"`.

## Marks

`trailing_stop_pending`
