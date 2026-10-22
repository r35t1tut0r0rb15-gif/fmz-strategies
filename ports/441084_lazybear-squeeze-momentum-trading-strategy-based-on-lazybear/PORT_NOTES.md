# #441084 基于LazyBear压缩动量指标的量化交易策略Squeeze-Momentum-Trading-Strategy-Based-on-LazyBear-Indicator -> `fmz_441084_squeeze_release_momentum_colour_tick_bracket`

- FMZ source id: 441084 (lineage).
- Source: https://www.fmz.com/strategy/441084 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-05 14:48:01). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C146). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry from signal-bar data |
| 2 | ADAPT | Tick bracket -> ATR multiples |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [12, 20] x `length_kc` [16, 20]: **4 trials**; multipliers and the ATR multiples fixed.

## Ambiguities resolved

- Tick bracket as ATR multiples (0.2 / 0.333 at the 2-hour reading); trail_points without trail_offset read as no trail. REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_squeeze"`.

## Marks

`coarse_bar_stop`
