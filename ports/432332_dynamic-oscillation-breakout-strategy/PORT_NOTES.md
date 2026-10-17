# #432332 Dynamic Oscillation Breakout Strategy -> `fmz_432332_donchian_sma_trend_long`

- FMZ source id: 432332 (lineage).
- Source: https://www.fmz.com/strategy/432332 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-11-16 15:40:25). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C51). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; stop fixed at entry (the re-set pending) |
| 2 | PASS | ATR stop, channel and SMA rules |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The margin settings stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`channel` [20, 55] x `sl_atr` [3.0, 1.5]: **4 trials**; SMA 8 / 32 and ATR 14 fixed.

## Ambiguities resolved

- Pending (not emitted as written): the stop re-set on each later breakout. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "donchian_breakout"`.

## Marks

`trailing_stop_pending, coarse_bar_stop`
