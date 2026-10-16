# #429385 MACD动量策略MACD-Momentum-Strategy -> `fmz_429385_macd_cross_long`

- FMZ source id: 429385 (lineage).
- Source: https://www.fmz.com/strategy/429385 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-10-16 15:57:34). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C23). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the moving tick bracket is not emitted (rule 2). |
| 2 | PASS | MACD crosses only (the tick bracket is not ported). |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code; the bracket is quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [12, 8] x `slow` [26, 50]: **4 trials**; signal 9 fixed.

## Ambiguities resolved

- Pending (not emitted): every bar a stop `lowest(low, 1)` ticks and a target `highest(high, 3)` ticks
  from the entry price (price levels used as tick counts), re-issued each bar.
- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`trailing_stop_pending`
