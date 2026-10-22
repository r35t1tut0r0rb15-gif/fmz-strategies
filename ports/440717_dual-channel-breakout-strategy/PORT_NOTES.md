# #440717 Dual Channel Breakout Strategy -> `fmz_440717_bb_kc_double_extreme_tick_bracket`

- FMZ source id: 440717 (lineage).
- Source: https://www.fmz.com/strategy/440717 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-01 14:43:07). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C139). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | ADAPT | Tick bracket -> ATR multiples |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`k_sl` [0.002, 0.4] x `bb_dev` [2.0, 1.5]: **4 trials**; target = 0.5 x stop; the lengths fixed.

## Ambiguities resolved

- Tick bracket as ATR multiples. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`coarse_bar_stop`
