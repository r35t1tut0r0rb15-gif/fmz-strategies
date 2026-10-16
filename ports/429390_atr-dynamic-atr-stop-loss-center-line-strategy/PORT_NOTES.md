# #429390 动态ATR止损中心线策略Dynamic-ATR-Stop-Loss-Center-Line-Strategy -> `fmz_429390_cog_bands_atr_stop`

- FMZ source id: 429390 (lineage).
- Source: https://www.fmz.com/strategy/429390 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-16 16:20:06). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C24). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; stop fixed at entry (approximations stated). |
| 2 | PASS | Percentage bands and a true-range multiple. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The strategy() 100 % of equity and commission stored; the stop quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND427304. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`percent` [6.0, 3.0] x `atr_mult` [2.0, 3.0]: **4 trials**; linreg 25 / 5 and ATR period 1 fixed.

## Ambiguities resolved

- Stop arming and re-entry levels approximated as stated. REVERSAL INTENDED. Mark coarse_bar_stop. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion_band"`.

## Marks

`coarse_bar_stop`
