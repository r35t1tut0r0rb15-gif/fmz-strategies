# #428853 RSI追踪ADX策略RSI-Tracking-ADX-Strategy -> `fmz_428853_adx_rsi_trend_long`

- FMZ source id: 428853 (lineage).
- Source: https://www.fmz.com/strategy/428853 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-10-10 10:32:48). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C21). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the conditional stop orders are not emitted (rule 2). |
| 2 | PASS | ADX and RSI levels only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code; the conditional stops are quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`adx_step` [0.2, 0.5] x `rsi_exit` [75, 70]: **4 trials**; ADX 14 / 14, RSI 14 / 9, SMA 20 fixed.

## Ambiguities resolved

- Pending stops (not emitted): (a) on a bar with rsi9 > 75 and dADX > 0.2 a sell stop at the average
  entry price + 4 x that bar's true range (it fills at once when the price is below that level);
  (b) on a bar where the SMA 20 falls, a sell stop at that bar's SMA 20 (the same order id, so the
  later call replaces the earlier level). Both persist until filled or replaced.
- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "directional_movement"`.

## Marks

`trailing_stop_pending`
