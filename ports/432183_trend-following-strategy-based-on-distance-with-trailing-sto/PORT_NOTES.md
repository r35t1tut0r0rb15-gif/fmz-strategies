# #432183 Trend Following Strategy Based on Distance with Trailing Stop Loss -> `fmz_432183_noro_distance_fade`

- FMZ source id: 432183 (lineage).
- Source: https://www.fmz.com/strategy/432183 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-11-15 11:24:16). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C49). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Close-to-close distance against its own average, RSI levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity, the capital % input and the martingale lot stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_len` [7, 14] x `dist_mult` [2.0, 1.5]: **4 trials**; the 30-bar distance average and the RSI limit 30 fixed.

## Ambiguities resolved

- close_all after an entry leaves the bar flat; adds and the martingale are sizing. FREQ = "3min".

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`
