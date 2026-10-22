# #442930 Dynamic Trailing Take Profit Trading Strategy -> `fmz_442930_sma14_28_cross_trailing_take_profit_pending`

- FMZ source id: 442930 (lineage).
- Source: https://www.fmz.com/strategy/442930 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-27 14:43:17). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C163). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the moving take-profit described (pending) |
| 2 | PASS | SMA crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Margin, quantity and capital stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND438046. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [14, 9] x `slow` [28, 50]: **4 trials**; the ATR settings fixed (pending).

## Ambiguities resolved

- The re-set take-profit pending. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`trailing_stop_pending`
