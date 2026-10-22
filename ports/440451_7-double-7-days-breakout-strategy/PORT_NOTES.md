# #440451 双7日突破策略Double-7-Days-Breakout-Strategy -> `fmz_440451_double_sevens_long`

- FMZ source id: 440451 (lineage).
- Source: https://www.fmz.com/strategy/440451 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-30 16:49:01). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C134). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Close bands and SMA |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity is sizing. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`value1` [7, 5] x `value2` [7, 10]: **4 trials**; SMA 200 fixed.

## Ambiguities resolved

- Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

`none`
