# #430374 Oscillation Breakthrough Strategy -> `fmz_430374_connors_rsi2_pullback_long`

- FMZ source id: 430374 (lineage).
- Source: https://www.fmz.com/strategy/430374 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-10-27 16:32:19). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C35). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | RSI levels and moving averages. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity per entry stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_level` [10, 5] x `long_ma` [200, 100]: **4 trials**; SMA 5, RSI average 4 / 30 fixed.

## Ambiguities resolved

- Entry and close on one bar: flat if already long, long if flat. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
