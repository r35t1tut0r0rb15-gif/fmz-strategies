# #439354 Aroon Williams MA BB ADX Powerful Multi indicator Strategy -> `fmz_439354_aroon_williams_adx_score_long`

- FMZ source id: 439354 (lineage).
- Source: https://www.fmz.com/strategy/439354 (PineScript v3, author ChaoZhang, FMZ last
  modified 2024-01-19 14:55:03). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C120). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Aroon, Williams %R, Bollinger basis and ADX levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`pos_wil` [-99, -90] x `pos_aroon1` [-85, -70]: **4 trials**; the other lengths and positions fixed.

## Ambiguities resolved

- Constant +3 terms and the warm-up scores as written. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`
