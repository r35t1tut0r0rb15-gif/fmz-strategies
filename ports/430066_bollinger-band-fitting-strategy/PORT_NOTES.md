# #430066 Bollinger Band Fitting Strategy -> `fmz_430066_noro_wizard_v11`

- FMZ source id: 430066 (lineage).
- Source: https://www.fmz.com/strategy/430066 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-10-24 16:52:52). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C32). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; adds not ported. |
| 2 | PASS | Bollinger bands, an RSI and body ratios. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The capital % lot and pyramiding 10 stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND430066. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [40, 20] x `rsi_limit` [30, 20]: **4 trials**; BB multiplier 2, RSI 7, body average 10 fixed.

## Ambiguities resolved

- Adds (pyramiding 10) not ported. Signal and exit on one bar: flat if already long, long if flat.
- Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`
