# #427989 ADX RSI Strategy -> `fmz_427989_adx_rsi_reversed`

- FMZ source id: 427989 (lineage).
- Source: https://www.fmz.com/strategy/427989 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-27 16:27:39). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C15). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders (the off swing exits aside). |
| 2 | PASS | Oscillator levels only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Equity quantity and swing exit inputs stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`adx_level` [30, 20] x `ob` [80, 70] x `os` [30, 20]: **8 trials**; defaults 30 / 80 / 30 (the source's); RSI 7, ADX 14 / 14 fixed.

## Ambiguities resolved

- Defaults kept: reverse on (RSI > 80 goes long), swing exits off (when on, their levels come from the fill bar: not ported), direction all.
- ADX as written (rma of tr, fixnan). REVERSAL INTENDED. FREQ = "15min".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator_turn"`.

## Marks

`none`
