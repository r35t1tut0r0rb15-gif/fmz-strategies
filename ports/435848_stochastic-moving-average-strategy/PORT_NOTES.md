# #435848 Stochastic Moving Average Strategy -> `fmz_435848_stoch_cross_ema_retrace_bracket`

- FMZ source id: 435848 (lineage).
- Source: https://www.fmz.com/strategy/435848 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-19 11:41:40). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C82). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | PASS | Stochastic cross, an EMA zone and an ATR bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The cash order size and risk-sizing inputs stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_mult` [1.0, 2.0] x `rr` [1.0, 2.0]: **4 trials**; stochastic 14 / 3, levels 80 / 20 and EMA 21 / 50 fixed.

## Ambiguities resolved

- Bracket re-based on the fill; entry only from flat; reference-market filter off. Opposite entries cannot occur. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "stochastic_oscillator"`.

## Marks

`none`
