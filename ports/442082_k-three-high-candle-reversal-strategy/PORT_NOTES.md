# #442082 三高K线反转策略Three-High-Candle-Reversal-Strategy -> `fmz_442082_three_green_modest_rise_close_tests_long`

- FMZ source id: 442082 (lineage).
- Source: https://www.fmz.com/strategy/442082 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-19 10:51:40). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C150). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | ADAPT | Openprofit in price units -> fraction of the close |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The fixed quantity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`target` [0.01, 0.02] x `stop` [0.004, 0.01]: **4 trials**; the span band and the gain fraction fixed.

## Ambiguities resolved

- Close-vs-fill exits; openprofit as a price fraction at BTC 42000. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`
