# #442377 Dual Moving Average Strategy -> `fmz_442377_sma_hl_envelope_rsi_extreme_long_tick_bracket`

- FMZ source id: 442377 (lineage).
- Source: https://www.fmz.com/strategy/442377 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-21 14:43:26). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C155). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry from signal-bar data |
| 2 | ADAPT | Tick bracket -> ATR multiples |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [5, 10] x `rsi_len` [5, 14]: **4 trials**; levels and the ATR multiples fixed.

## Ambiguities resolved

- Both entries buy (direction 1, as written); tick bracket as ATR multiples. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
