# #488020 多指标确认动态追踪突破量化交易策略-Multi-Indicator-Confirmation-Dynamic-Trailing-Breakout-Quantitative-Trading-Strategy -> `fmz_488020_ema40_breakdown_atr_time_exit`

- FMZ source id: 488020 (lineage).
- Source: https://www.fmz.com/strategy/488020 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-03-24 14:20:27). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L12). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; stop fixed at the signal bar. |
| 2 | PASS | EMAs, ATR and bar counts. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The risk / leverage quantity quoted; the stop via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_atr` [1.2, 2.0] x `max_hold` [72, 36]: **4 trials**; defaults 1.2 / 72 (the source's); EMA 15 / 40 and ATR 14
fixed.

## Ambiguities resolved

- `macdLine_1h := macdLine_1h[1]` (and the signal line) reassigns each variable to its own previous value: na on the
  first bar, so na forever. `trendUp_1h` is never true and `breakoutLong` never fires: short only as written.
- The stop variable ratchets while short, but `strategy.exit` is called only with the entry: the stop stays at the
  signal bar's 1.2 ATR (exact, no mark). Entries only from flat: `simulate()` mirrors the stop (#430254). The time
  exit counts from the last signal bar and is a close-based exit signal. Opposite entries cannot occur. Stop module:
  `portfolio_kwargs` {} (D4). FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_breakout"`.

## Marks

`none`
