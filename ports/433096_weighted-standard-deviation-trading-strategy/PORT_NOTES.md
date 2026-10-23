# #433096 Weighted Standard Deviation Trading Strategy -> `fmz_433096_volume_weighted_sd_band_touch_pct_bracket_reversal`

- FMZ source id: 433096 (lineage).
- Source: https://www.fmz.com/strategy/433096 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-24 13:54:58). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V14). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; percent bracket from the fill |
| 2 | PASS | Volume-weighted band touches |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Strategy(): 20 % of equity, capital 10000, commission 0.075 %, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 50] x `band_mult` [2.0, 2.5]: **4 trials**; SL 3.11 %, TP 7.5 %.

## Ambiguities resolved

- Later call wins on a two-sided bar; bracket from the fill. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "45min".

## FAMILY (proposed, user to confirm)

`FAMILY = "weighted_bands"`.

## Marks

`none`
