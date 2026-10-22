# #477579 Bollinger Bands Breakout Momentum Trading Strategy -> `fmz_477579_bb20_upper_break_lower_close_long`

- FMZ source id: 477579 (lineage).
- Source: https://www.fmz.com/strategy/477579 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-01-06 15:19:50). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C234). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Bollinger band breakouts |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Qty 1 and capital 100000 stored, not ported; costs not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 50] x `mult` [2.0, 1.5]: **4 trials**; SMA basis.

## Ambiguities resolved

- SMA basis (default). Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_breakout"`.

## Marks

`none`
