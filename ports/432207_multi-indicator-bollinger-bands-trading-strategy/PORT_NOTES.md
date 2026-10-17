# #432207 Multi Indicator Bollinger Bands Trading Strategy -> `fmz_432207_one_sigma_band_breakout_basis_exit`

- FMZ source id: 432207 (lineage).
- Source: https://www.fmz.com/strategy/432207 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-11-15 15:30:43). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C49). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Band and basis crosses |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity and the commission stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [34, 20, 50]: **3 trials**; the 1 sd band fixed.

## Ambiguities resolved

- Inert RSI / MACD layers (repeated ids, non-existent ids). A same-side breakout while in the trade closes it. REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_breakout"`.

## Marks

`none`
