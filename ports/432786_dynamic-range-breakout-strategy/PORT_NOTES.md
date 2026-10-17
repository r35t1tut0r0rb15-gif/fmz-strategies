# #432786 Dynamic Range Breakout Strategy -> `fmz_432786_noro_wizard_band_dip`

- FMZ source id: 432786 (lineage).
- Source: https://www.fmz.com/strategy/432786 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-12-01 15:00:31). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C54). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | A band of the lows and the body against its own average |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity, the capital % input, the lot and pyramiding stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND430066. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [25, 15] x `mult` [2.0, 1.5]: **4 trials**; the body average 10 fixed.

## Ambiguities resolved

- close_all after the entry leaves a green signal bar flat. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`
