# #474850 Multi Market Adaptive Multi Indicator Trend Following Strategy -> `fmz_474850_coppock_zero_cross_cmf_dpo_atr_bracket_reversal`

- FMZ source id: 474850 (lineage).
- Source: https://www.fmz.com/strategy/474850 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-12 15:23:28). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V35). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; ATR bracket at the signal close as fractions of the fill |
| 2 | PASS | Coppock zero crossings confirmed by CMF and DPO |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Risk-based qty, leverage and 10 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_atr` [2.0, 1.5] x `tp_atr` [3.0, 4.5]: **4 trials**; CMF 20, DPO 21, Coppock 11 / 14 / 10, ATR 14.

## Ambiguities resolved

- Bracket at the signal close. Volume = broker tick volume (CMF). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "coppock"`.

## Marks

`coarse_bar_stop`
