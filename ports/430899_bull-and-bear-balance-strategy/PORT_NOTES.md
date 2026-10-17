# #430899 Bull and Bear Balance Strategy -> `fmz_430899_bull_bear_balance`

- FMZ source id: 430899 (lineage).
- Source: https://www.fmz.com/strategy/430899 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-11-02 17:12:40). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C42). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | ADAPT | Price-unit levels -> ATR fractions |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`level_atr` [0.015, 0.25] x `atr_len` [14, 28]: **4 trials**; the symmetric levels (sell = -buy) fixed.

## Ambiguities resolved

- Price-unit levels as ATR fractions (criterion 2 ADAPT). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator_turn"`.

## Marks

`none`
