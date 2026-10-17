# #482830 基于布林带动态均值突破的量化交易策略-Dynamic-Bollinger-Bands-Breakout-Quantitative-Trading-Strategy -> `fmz_482830_bb_upper_breakout_lower_exit_long_2d`

- FMZ source id: 482830 (lineage).
- Source: https://www.fmz.com/strategy/482830 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-20 14:51:24). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L30). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bollinger bands. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity; the commission is a cost (not ported). |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ma_type` ["SMA", "EMA"] x `mult` [2.0, 2.5]: **4 trials**; defaults SMA / 2 (the source's); length 20 fixed.

## Ambiguities resolved

- The basis-type input only switches the average: SMA and EMA are variants; VWMA (volume, check 8) is not offered;
  RMA and WMA are left out of the grid. The plot offset input does not touch the signals.
- Long only. Two-day bars: blocks of broker-day dates from 1970-01-01 (decision owed, #426509).

## FAMILY (proposed, user to confirm)

`FAMILY = "breakout"`.

## Marks

none
