# #482512 QFL震荡条件止损均线策略-QFL-Oscillation-Stop-Loss-Moving-Average-Strategy -> `fmz_482512_qfl_base50_panic_break_cooldown5_rebound_exit_long`

- FMZ source id: 482512 (lineage).
- Source: https://www.fmz.com/strategy/482512 (PineScript v6, author ChaoZhang, FMZ last
  modified 2025-02-18 18:18:01). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C246). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; exit on a percent gain over the entry price |
| 2 | PASS | Base-break dip buying with a rebound exit |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`look_back_period` [50, 100] x `exit_profit_threshold` [0.01, 0.03]: **4 trials**; ATR 14 x 1.2, panic 0.5 %, rebound 0.8, cooldown 5.

## Ambiguities resolved

- The panic flag is never cleared and the cooldown restarts while a long is held, as written.
- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "support_resistance"`.

## Marks

`none`
