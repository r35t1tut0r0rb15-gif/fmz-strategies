# #430368 Reversal Breakout Strategy -> `fmz_430368_bb_stoch_scalp_tick_bracket`

- FMZ source id: 430368 (lineage).
- Source: https://www.fmz.com/strategy/430368 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-27 16:14:16). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C35). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the shared-id exit read as written, the moving stop fixed at the fill. |
| 2 | ADAPT | Tick stop / target -> ATR fractions. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code; the tick exits quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_atr` [0.0003, 0.05] x `tp_atr` [0.005, 0.5]: **4 trials**; BB 20 / 2 and stochastic 14 / 5 / 3 fixed.

## Ambiguities resolved

- Pending (as written, not emitted for longs): the shared exit id leaves longs without an exit; the short's stop is
  re-issued from each close (moving) and fixed at the fill here.
- Ticks -> ATR. Mark coarse_bar_stop. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`trailing_stop_pending, coarse_bar_stop`
