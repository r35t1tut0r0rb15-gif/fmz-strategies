# #427458 AK Dual RSI Breakout Strategy -> `fmz_427458_ak_rsi2_as_written`

- FMZ source id: 427458 (lineage).
- Source: https://www.fmz.com/strategy/427458 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-09-21 11:51:01). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C8). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | MA lengths, RSI levels. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`long_level` [5, 10] x `short_level` [90, 95] x `ma_long` [200, 100]: **8 trials**; defaults 5 / 90 / 200 (the source's); RSI 2, SMA 5 fixed.

## Ambiguities resolved

- **As written**, both `close_all` lines close any open position (above or below SMA 5): positions last about one bar after the fill. **Decision owed:** port the evidently intended per-side exits as a separate module.
- REVERSAL INTENDED. FREQ = "1h" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
