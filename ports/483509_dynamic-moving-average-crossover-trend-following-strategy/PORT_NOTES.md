# #483509 Dynamic Moving Average Crossover Trend Following Strategy -> `fmz_483509_ema13_21_sma120_cross_ema_dist_bracket_profit_trigger_flat`

- FMZ source id: 483509 (lineage).
- Source: https://www.fmz.com/strategy/483509 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-24 09:46:10). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C259). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket as fractions of the fill, profit trigger as an exit signal |
| 2 | PASS | EMA / SMA crossings with an EMA-distance bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity and capital stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sma_length` [120, 60] x `ema_fast_period` [13, 9]: **4 trials**; EMA 21, stop floor 0.2 %, target 5 x stop, trigger 0.8 %.

## Ambiguities resolved

- The trail's marketable target closes the trade at the next open once +0.8 % is reached, as written.
- The flat gate is followed in a loop. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
