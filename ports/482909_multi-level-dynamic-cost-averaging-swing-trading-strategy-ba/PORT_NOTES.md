# #482909 基于相对强弱指数和平均真实波幅的多层次动态成本均摊波段交易策略-Multi-Level-Dynamic-Cost-Averaging-Swing-Trading-Strategy-Based-on-RSI-and-ATR -> `fmz_482909_rsi_oversold_avg_signal_atr_target_long`

- FMZ source id: 482909 (lineage).
- Source: https://www.fmz.com/strategy/482909 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-27 17:22:25). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L24). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the close-based target is an exit signal. |
| 2 | PASS | RSI and ATR multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The $200-risk qty quoted, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tp_atr` [3.0, 2.0] x `rsi_os` [30, 35]: **4 trials**; defaults 3 / 30 (the source's); RSI 14, ATR 14 and the 4-buy
cap fixed.

## Ambiguities resolved

- Default pyramiding (1): the later "DCA" buys add nothing (and adds would be sizing, #490570); the script's average
  of the buy-signal closes still sets the exit, as written.
- The target is checked on closes through `strategy.close`: an exit signal at the next open (rule 3); a target met on
  a buy-signal bar resets the count without an exit signal (the position is not yet open in Pine on the first buy).
- Long only: opposite entries cannot occur. No stops. Broker days stamped with their first minute (as #430984).
  FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

`none`
