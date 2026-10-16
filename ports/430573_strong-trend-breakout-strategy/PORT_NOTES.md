# #430573 Strong Trend Breakout Strategy -> `fmz_430573_donchian_wicks_long`

- FMZ source id: 430573 (lineage).
- Source: https://www.fmz.com/strategy/430573 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-30 14:53:32). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C36). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the moving levels fixed at entry (rule 2). |
| 2 | PASS | Channels of bar extremes and a percentage stop. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 50] x `stop_pct` [1.0, 2.0]: **4 trials**.

## Ambiguities resolved

- Pending (not emitted as written): the target and the stop move every bar in the source; fixed at entry here.
- Long only. FREQ = "5min".

## FAMILY (proposed, user to confirm)

`FAMILY = "donchian_breakout"`.

## Marks

`trailing_stop_pending`
