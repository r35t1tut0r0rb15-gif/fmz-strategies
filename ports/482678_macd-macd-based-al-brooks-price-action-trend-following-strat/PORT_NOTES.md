# #482678 MACD结合阿尔布鲁克斯价格行为的趋势跟踪策略-MACD-Based-Al-Brooks-Price-Action-Trend-Following-Strategy -> `fmz_482678_sma52_macd_state_pct_bracket`

- FMZ source id: 482678 (lineage).
- Source: https://www.fmz.com/strategy/482678 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-19 17:36:15). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L32). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the re-issued bracket fixed at entry (marked). |
| 2 | PASS | An SMA, MACD and percentage distances. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Default quantity; the bracket via `stops()`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`candle` ["close", "open"] x `sl_buffer` [0.01, 0.02]: **4 trials**; defaults close / 0.01 (the source's); SMA 52,
MACD 12 / 26 / 9 and RR 2 fixed.

## Trailing stop (mark `trailing_stop_pending`)

buy / sell are states: every bar in them re-issues `strategy.exit` from that bar's close, so the bracket moves with
the price. The port fixes it at the entry's signal close (re-based on the fill).

## Ambiguities resolved

- The buffer 0.01 ("in %") is used as a fraction: 1 % stop, 2 % target.
- The closes run only on bars in neither state, so they never meet an entry; `simulate()` mirrors the house bracket
  from the fill (as #430254), and a stopped trade re-enters on the next bar still in the state.
- REVERSAL INTENDED. Stop module: `portfolio_kwargs` {} (D4). Daily bars: broker days stamped with their first
  minute.

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_following"`.

## Marks

`coarse_bar_stop`, `trailing_stop_pending`
