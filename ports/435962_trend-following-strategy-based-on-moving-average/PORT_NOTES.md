# #435962 Trend Following Strategy Based on Moving Average -> `fmz_435962_minervini_template_long`

- FMZ source id: 435962 (lineage).
- Source: https://www.fmz.com/strategy/435962 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-20 14:23:49). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C84). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; exits on closes |
| 2 | PASS | Average stack and percent rules |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The commission input stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`take` [1.1, 1.2] x `stop` [0.95, 0.9]: **4 trials**; the 260-bar window and the 25 % limits fixed.

## Ambiguities resolved

- Close-based exits on the average price; re-entry on the next flat bar. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_confluence"`.

## Marks

`none`
