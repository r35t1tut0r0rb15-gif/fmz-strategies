# #434989 突破重叠K线高低位策略Inside-Bar-Range-Breakout-Strategy -> `fmz_434989_bar_breakout_atr_bracket`

- FMZ source id: 434989 (lineage).
- Source: https://www.fmz.com/strategy/434989 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-11 15:16:53). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C72). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket from the signal bar (re-issued levels approximated) |
| 2 | PASS | Bar breakouts and ATR exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_mult` [2.0, 1.0] x `tp_mult` [3.0, 1.5]: **4 trials**; ATR 14 and the 20-bar look back fixed.

## Ambiguities resolved

- Signal-bar ATR bracket re-based on the fill; unused inside-bar test dropped. Marks trailing_stop_pending, coarse_bar_stop. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_breakout"`.

## Marks

`trailing_stop_pending, coarse_bar_stop`
