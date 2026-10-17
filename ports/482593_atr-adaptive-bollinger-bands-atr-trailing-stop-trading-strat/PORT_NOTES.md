# #482593 自适应布林带ATR跟踪止损交易策略-Adaptive-Bollinger-Bands-ATR-Trailing-Stop-Trading-Strategy -> `fmz_482593_bb_reentry_close_atr_trail`

- FMZ source id: 482593 (lineage).
- Source: https://www.fmz.com/strategy/482593 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-02-19 11:00:57). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L33). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; a close-based trail. |
| 2 | PASS | Bollinger bands and ATR multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Default quantity. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_mult` [3.0, 2.0] x `bb_mult` [2.0, 1.5]: **4 trials**; defaults 3 / 2 (the source's); BB 20 and ATR 14 fixed.

## Ambiguities resolved

- The trail is computed and crossed on closes and acted on with `strategy.close`: a close-based exit signal at the
  next open (rule 3), no mark. It starts on the fill bar (`strategy.position_size` already set there).
- The closes act on the position held at the bar's start and never undo an entry on that bar (#430850).
- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

none
