# #439200 Multi factor Moving Average Trend Following Strategy -> `fmz_439200_rising_averages_long_flagged`

- FMZ source id: 439200 (lineage).
- Source: https://www.fmz.com/strategy/439200 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-18 12:07:52). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C117). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-tested stop |
| 2 | PASS | Slope tests of averages and MACD |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The 1000 / close position size stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND428579. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`stop_loss` [5.0, 2.0] x `sma_len` [100, 50]: **4 trials**; EMA 20, SMA 200 and MACD 12 / 26 / 7 fixed.

## Ambiguities resolved

- The script's flag gates trades; close-tested stop from the signal close. Long only. FREQ = "10min".

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_confluence"`.

## Marks

`none`
