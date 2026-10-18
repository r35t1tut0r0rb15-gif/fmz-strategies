# #436519 Low Lag Triple Moving Average Fast Trading Strategy -> `fmz_436519_low_lag_ma_cross_bracket`

- FMZ source id: 436519 (lineage).
- Source: https://www.fmz.com/strategy/436519 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-25 14:24:38). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C91). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | ADAPT | Tick amounts -> ATR multiples |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The tick inputs and the lot formula stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`mav` ["temadelay", "emadelay"] x `k_atr` [0.03, 0.5]: **4 trials**; the target is 200 / 130 of the stop; N 8 and K 1.2 fixed.

## Ambiguities resolved

- Tick amounts -> ATR multiples. Six average types are ported; two are searched. REVERSAL INTENDED. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop`
