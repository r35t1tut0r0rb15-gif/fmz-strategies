# #482457 ATR动态趋势跟踪与重入场交易策略-ATR-Dynamic-Trend-Following-with-Re-entry-Trading-Strategy -> `fmz_482457_sma_high_atr_band_break_bracket_long`

- FMZ source id: 482457 (lineage).
- Source: https://www.fmz.com/strategy/482457 (PineScript v6, author ChaoZhang, FMZ last
  modified 2025-02-18 15:11:28). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L35). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders and a bracket set at entry. |
| 2 | PASS | SMAs and a smoothed ATR band. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Default quantity; the bracket via `stops()`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [10, 20] x `tp_band` [5, 3]: **4 trials**; defaults 10 / 5 (the source's); ATR 200 smoothed 200, x 0.8,
and the 2-band stop fixed.

## Ambiguities resolved

- The re-entry needs `close == entryPrice`, na after every exit: inert. `signal_down` is only drawn.
- `inTrade` clears only on a close beyond the signal-close levels (as written), so a stop filled inside a bar
  without such a close blocks new entries until one comes.
- Long only. Stop module: `portfolio_kwargs` {} (D4). Daily bars: broker days stamped with their first minute.

## FAMILY (proposed, user to confirm)

`FAMILY = "breakout"`.

## Marks

`coarse_bar_stop`
