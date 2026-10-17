# #483510 多重时序趋势甄别型自适应动态调仓策略-Multi-Temporal-Trend-Identification-Adaptive-Position-Management-Strategy -> `fmz_483510_supertrend_cross_dema_filter_reversal`

- FMZ source id: 483510 (lineage).
- Source: https://www.fmz.com/strategy/483510 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-27 16:49:07). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L18). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Supertrend (ATR bands) and a DEMA. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing in the source. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`factor` [3.0, 2.0] x `allow_short` [True, False]: **4 trials**; defaults 3 / True (the source's); ATR 10 and DEMA 100
fixed; `allowLong` stays True.

## Ambiguities resolved

- `ta.supertrend` as TradingView documents it (`pine_supertrend`); the line is na on the first bar, as written.
- A cross against the DEMA filter (or a short signal with shorts off) only closes the opposite position.
- REVERSAL INTENDED; an exit is never emitted with the opposite entry on one bar. No stops. FREQ = "5min".

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`
