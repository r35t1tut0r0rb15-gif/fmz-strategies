# #432095 Momentum Squeeze Strategy -> `fmz_432095_squeeze_momentum_zero_cross_mfi58_pct_bracket_reversal`

- FMZ source id: 432095 (lineage).
- Source: https://www.fmz.com/strategy/432095 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-14 14:04:24). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V12). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket at the signal close as fractions of the fill |
| 2 | PASS | Squeeze momentum zero crossings with a money-flow filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Strategy(): 100 % of equity, capital 100000, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`mom_len` [20, 14] x `mfi_len` [58, 30]: **4 trials**; SL 50 %, TP 50 %.

## Ambiguities resolved

- mf as the formula only. Bracket at the signal close. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "squeeze_momentum"`.

## Marks

`coarse_bar_stop`
