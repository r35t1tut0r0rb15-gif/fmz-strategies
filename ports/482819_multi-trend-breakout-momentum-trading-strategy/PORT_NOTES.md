# #482819 Multi Trend Breakout Momentum Trading Strategy -> `fmz_482819_breakout_ema_stack_consolidation_short_ema200_exit`

- FMZ source id: 482819 (lineage).
- Source: https://www.fmz.com/strategy/482819 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-20 14:53:56). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V40). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Volume breakouts in an EMA stack, consolidation shorts, EMA 200 exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`breakout` [20, 55] x `narrow` [0.5, 1.0]: **4 trials**; range 10, EMA 30 / 50 / 200, volume x 2.

## Ambiguities resolved

- Entries only from flat; the later short wins on a two-sided bar. Volume = broker tick volume. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "channel_breakout"`.

## Marks

`none`
