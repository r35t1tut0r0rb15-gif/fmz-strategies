# #430844 三重RSI极值交易策略Triple-RSI-Extremum-Trading-Strategy -> `fmz_430844_noro_triple_rsi_extremes`

- FMZ source id: 430844 (lineage).
- Source: https://www.fmz.com/strategy/430844 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-11-02 14:34:21). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C40). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | RSI levels and bar colour. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity per entry stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`accuracy` [3, 5, 1]: **3 trials**; RSI 2 / 7 / 14 fixed.

## Ambiguities resolved

- Only longs have the bar-colour exit, as written. REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
