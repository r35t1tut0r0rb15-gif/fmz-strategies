# #434710 月末动量突破200日均线策略End-of-Month-Breakout-on-200-Day-Moving-Average-Strategy -> `fmz_434710_day30_sma200_long`

- FMZ source id: 434710 (lineage).
- Source: https://www.fmz.com/strategy/434710 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-08 16:02:08). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C71). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Price against an average on a calendar day |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The strategy() 100 % of equity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`dom` [30, 28] x `sma_len` [200, 100]: **4 trials**.

## Ambiguities resolved

- Day 30 of the broker day's date; date window dropped. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "calendar_seasonal"`.

## Marks

`none`
