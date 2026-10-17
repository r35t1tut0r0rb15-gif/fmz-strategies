# #433022 Buying dips with take profit and stop loss -> `fmz_433022_buy_the_dip_atr_bracket`

- FMZ source id: 433022 (lineage).
- Source: https://www.fmz.com/strategy/433022 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-23 16:50:01). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C57). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | PASS | A channel break and ATR exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code; the bracket quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_atr` [2.0, 1.0] x `tp_atr` [1.0, 2.0]: **4 trials**; channel 7 and ATR 15 fixed.

## Ambiguities resolved

- Bracket from the signal day's ATR, re-based on the fill. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "donchian_breakout"`.

## Marks

`coarse_bar_stop`
