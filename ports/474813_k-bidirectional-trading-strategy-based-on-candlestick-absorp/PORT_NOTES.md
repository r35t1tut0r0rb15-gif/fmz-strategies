# #474813 基于K线蜡烛图吸收形态的双向交易量化策略-Bidirectional-Trading-Strategy-Based-on-Candlestick-Absorption-Pattern-Analysis -> `fmz_474813_candle_absorption_low_volume_reversal`

- FMZ source id: 474813 (lineage).
- Source: https://www.fmz.com/strategy/474813 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-12 11:27:27). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V35). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Absorption candles on falling volume |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`body_ratio` [1.0, 1.5]: **2 trials**; volume over 3 bars.

## Ambiguities resolved

- Flags only block repeats. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "candlestick_pattern"`.

## Marks

`none`
