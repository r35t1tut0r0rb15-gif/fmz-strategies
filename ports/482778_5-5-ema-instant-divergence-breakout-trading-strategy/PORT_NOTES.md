# #482778 5均线即时背离突破交易策略-5-EMA-Instant-Divergence-Breakout-Trading-Strategy -> `fmz_482778_bar_beyond_ema5_range_bracket`

- FMZ source id: 482778 (lineage).
- Source: https://www.fmz.com/strategy/482778 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-27 17:50:24). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L32). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the re-placed bracket fixed at entry (marked). |
| 2 | PASS | An EMA and the signal bar's range. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Default quantity; the bracket via `stops()`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_len` [5, 10] x `target_mult` [3.0, 1.5]: **4 trials**; defaults 5 / 3 (the source's).

## Trailing stop (mark `trailing_stop_pending`)

Each signal bar re-issues `strategy.exit` with that bar's low / high and range, so a later same-side signal while
held moves the bracket. The port keeps the entry's levels.

## Ambiguities resolved

- The trigger is set and tested on the same bar's high (low), so every bar entirely beyond the EMA is a signal.
- A bar closing at its own low (high) gives a zero-length stop and emits no long (short) (as L2 #491035).
- REVERSAL INTENDED. Stop module: `portfolio_kwargs` {} (D4). Daily bars: broker days stamped with their first
  minute.

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

`coarse_bar_stop`, `trailing_stop_pending`
