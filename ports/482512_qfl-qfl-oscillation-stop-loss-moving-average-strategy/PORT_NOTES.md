# #482512 QFL震荡条件止损均线策略-QFL-Oscillation-Stop-Loss-Moving-Average-Strategy -> `fmz_482512_qfl_base_crack_rebound_exit_long`

- FMZ source id: 482512 (lineage).
- Source: https://www.fmz.com/strategy/482512 (PineScript v6, author ChaoZhang, FMZ last
  modified 2025-02-18 18:18:01). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L34). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; a close-based take profit. |
| 2 | PASS | Rolling extremes, ATR multiples and percentages. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Default quantity. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`lookback` [50, 20] x `profit` [0.01, 0.03]: **4 trials**; defaults 50 / 1 % (the source's); rebound 0.8, ATR 14 x
1.2, panic 0.5 %, range 3 bars and cooldown 5 fixed.

## Ambiguities resolved

- `panicSellMovement` is a `var` that is never reset: true for good after the first wide move (as written).
- The cooldown counts from every signal bar, held or not.
- One position (pyramiding 1): the average price is the fill. The take profit is checked on closes with
  `strategy.close`: exit signal at the next open (rule 3). The non-default "each_position" option (partial closes)
  is not ported. No stop. Long only. Daily bars: broker days stamped with their first minute.

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

none
