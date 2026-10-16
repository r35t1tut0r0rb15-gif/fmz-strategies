# #428619 Alpha RSI Breakout Trading Strategy -> `fmz_428619_alpha_rsi_breakout_long`

- FMZ source id: 428619 (lineage).
- Source: https://www.fmz.com/strategy/428619 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-10-07 15:45:07). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C18) AS WRITTEN. Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | RSI levels and MA length. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Commented strategy() settings stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_entry` [34, 40] x `sma_length` [200, 100]: **4 trials**; defaults 34 / 200 (the source's); RSI 14, exits 30 / 50 fixed.

## Ambiguities resolved

- The "trailing stop" (lowest close since entry, updated before the check) can never fire: not ported.
- Exits: RSI >= 50 or <= 30. strategy() commented out. Long only. Broker-day bars; FREQ = "1D".

## Decision owed

The intended trailing exit (probably the highest close since entry).

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator_turn"`.

## Marks

`none`
