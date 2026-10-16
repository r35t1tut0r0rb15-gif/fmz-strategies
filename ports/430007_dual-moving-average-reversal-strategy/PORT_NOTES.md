# #430007 Dual Moving Average Reversal Strategy -> `fmz_430007_noro_bands_scalper_v14`

- FMZ source id: 430007 (lineage).
- Source: https://www.fmz.com/strategy/430007 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-10-24 10:56:08). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C31). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar counts and ratios of averages, a percent take of 0. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity per trade stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND426995. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 10, 40] x `body_mult` [2.0, 1.0]: **6 trials**; defaults 20 / 2 (double body on, the source's); take 0 %, bands
entry on fixed.

## Ambiguities resolved

- Counter-trend entries (qty 0) only close the opposite position; the entry price is the next open after the signal.
- Same rules as #427185 (v1.6) except the body test: v1.4 compares the body with ema(body, 30) x 2 ("Double Body").
- REVERSAL INTENDED. FREQ = "1h" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_channel_breakout"`.

## Marks

`none`
