# #427313 Dual RSI Combined with Bollinger Band for Trend Following -> `fmz_427313_madrugada_dual_rsi_bb`

- FMZ source id: 427313 (lineage).
- Source: https://www.fmz.com/strategy/427313 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-09-19 22:10:02). Verbatim here as `original_source.md`. Read 2026-10-15 (FMZ-C).
- Status: PORTED (batch C5). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Oscillator levels, band in standard deviations. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`bb_length` [20, 40] x `bb_mult` [1.7, 2.2] x `rsi1_length` [10, 14]: **8 trials**; defaults 20 / 1.7 / 10 (the source's); RSI 6 and the hard-coded 30 / 27 / 70 thresholds fixed.

## Ambiguities resolved

- The OSold / OBought inputs are never used; the entry thresholds are constants in the functions.
- `exitLong()` is always true but never used by an order: the only exit is the opposite entry (REVERSAL INTENDED).
- FREQ = "2min" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`
