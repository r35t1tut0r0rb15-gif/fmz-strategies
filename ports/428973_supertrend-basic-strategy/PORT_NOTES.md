# #428973 SuperTrend Basic Strategy -> `fmz_428973_supertrend_pullback_bracket`

- FMZ source id: 428973 (lineage).
- Source: https://www.fmz.com/strategy/428973 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-10-11 15:14:54). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C22). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry. |
| 2 | PASS | An ATR multiple, RSI levels and percentages. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The commented-out strategy() stored; the bracket quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`factor` [3.0, 2.0] x `bracket_pct` [1.0, 2.0] (stop = target): **4 trials**; ATR 10, EMA 200, RSI 14 / 50 fixed.

## Ambiguities resolved

- Flat tracked through the house bracket on bars; entries from flat only.
- Mark coarse_bar_stop. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`coarse_bar_stop`
