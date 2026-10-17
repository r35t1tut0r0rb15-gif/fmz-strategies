# #488848 早盘高低点突破动态追踪策略-Opening-Bell-High-Low-Breakout-Dynamic-Trailing-Strategy -> `fmz_488848_0830_candle_breakout_tick_trail`

- FMZ source id: 488848 (lineage).
- Source: https://www.fmz.com/strategy/488848 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-31 11:21:39). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L8). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders and a close-checked trail; bracket fixed at the signal bar. |
| 2 | ADAPT | 15 / 30 ticks and the 100-unit stop -> ATR multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`session_tz` ["UTC", "America/Chicago"] x `trail_atr` [0.03, 0.5]: **4 trials**; defaults UTC / 0.03 (the source as
written); TP 0.06 ATR and SL 20 ATR fixed. On 5-minute ETH_USDT (tick 0.01, ATR about 5) 15 / 30 ticks are about
0.03 / 0.06 ATR and 100 price units about 20 ATR (judgement, stated before any backtest).

## Session open (check 9)

The 08:30 candle, the 08:40-15:00 entry window and the day reset are in the chart's time zone: UTC as written, or
08:30 America/Chicago (the US open, DST by the zone) as the variant. Decision owed: which reading to keep.

## Ambiguities resolved

- The tick trail is close-checked (no mark). One trade a day. REVERSAL INTENDED (only across days). FREQ = "5min".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_breakout"`.

## Marks

`none`
