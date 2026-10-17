# #481364 动量驱动型肯特纳通道突破交易策略-Momentum-Driven-Keltner-Channel-Breakout-Trading-Strategy -> `fmz_481364_keltner_break_momentum_ema_exit`

- FMZ source id: 481364 (lineage).
- Source: https://www.fmz.com/strategy/481364 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-02-10 15:03:16). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L38). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | A Keltner channel and momentum signs. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 200 % of equity. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`mult` [1.5, 2.5] x `mom_len` [14, 28]: **4 trials**; defaults 1.5 / 14 (the source's); KC length 20 fixed.

## Ambiguities resolved

- The closes act on the position held at the bar's start and never undo an entry on that bar (#430850).
- REVERSAL INTENDED. FREQ = "15min".

## FAMILY (proposed, user to confirm)

`FAMILY = "breakout"`.

## Marks

none
