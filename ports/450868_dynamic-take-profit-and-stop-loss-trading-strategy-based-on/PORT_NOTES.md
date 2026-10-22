# #450868 Dynamic Take Profit and Stop Loss Trading Strategy Based on Three Consecutive Bearish Candles and Moving Averages -> `fmz_450868_three_falling_closes_sma200_pct_bracket_sma10_exit_long`

- FMZ source id: 450868 (lineage).
- Source: https://www.fmz.com/strategy/450868 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-05-09 16:42:35). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C183). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed from the fill |
| 2 | PASS | Falling-close dips in an uptrend with a percent bracket and an SMA exit |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code; the percent bracket quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG450868. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`n_falls` [3, 4] x `tp` [0.015, 0.03]: **4 trials**; the stop 1 %, the SMA 200 and the SMA 10 fixed.

## Ambiguities resolved

- Bracket from the fill; followed in state for the from-flat entries. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

`coarse_bar_stop`
