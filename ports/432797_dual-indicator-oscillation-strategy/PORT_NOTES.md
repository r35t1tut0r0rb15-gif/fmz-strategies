# #432797 Dual Indicator Oscillation Strategy -> `fmz_432797_stoch_rsi_extreme_bracket`

- FMZ source id: 432797 (lineage).
- Source: https://www.fmz.com/strategy/432797 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-21 15:50:37). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C54). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry (the per-bar re-placement pending) |
| 2 | ADAPT | Price-unit distances -> ATR multiples |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code; the exits quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_atr` [4.0, 1.5] x `tp_atr` [4.0, 1.5]: **4 trials**; stochastic 14 / 3 / 3, RSI 14 and the levels fixed.

## Ambiguities resolved

- Pending (not emitted as written): the bracket re-placed every bar around the close. Price units as ATR. REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "stochastic_oscillator"`.

## Marks

`trailing_stop_pending`
