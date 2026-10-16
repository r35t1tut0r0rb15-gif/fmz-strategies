# #428051 RSI Signal Tracking Reversal Trading Strategy -> `fmz_428051_noro_anti_rsi`

- FMZ source id: 428051 (lineage).
- Source: https://www.fmz.com/strategy/428051 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-09-28 10:54:24). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C15). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | RSI levels and body ratio. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Lot, martingale and capital inputs stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_period` [14, 7] x `rsi_limit` [25, 15]: **4 trials**; defaults 14 / 25 (the source's); body SMA 10 fixed.

## Ambiguities resolved

- Entries only from flat: opposite entries cannot occur. Adds (up2 / dn2) ignored (pyramiding 0).
- Martingale, capital % and switches are sizing; date window dropped. FREQ = "15min".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator_turn"`.

## Marks

`none`
