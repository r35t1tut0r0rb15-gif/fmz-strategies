# #435288 Combination Reversal Strategy Based on Stochastic Turnaround Factor and Key Reversal Signal -> `fmz_435288_reversal_123_key_reversal_up`

- FMZ source id: 435288 (lineage).
- Source: https://www.fmz.com/strategy/435288 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-13 17:54:34). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C77). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | REVIEW | The short branch cannot occur: one-bar trades as written |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND426888. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`reverse` [False, True] x `n_length` [1, 5]: **4 trials**; stochastic 14 / 1 / 3 and level 50 fixed.

## Ambiguities resolved

- One-bar trades; no short branch in the combination. FREQ = "15min".

## FAMILY (proposed, user to confirm)

`FAMILY = "reversal_pattern"`.

## Marks

`none`
