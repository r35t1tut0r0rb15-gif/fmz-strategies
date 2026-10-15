# #427120 Noro Bands Trend Following Strategy -> `fmz_427120_noro_bands`

- FMZ source id: 427120 (lineage).
- Source: https://www.fmz.com/strategy/427120 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-09-18 13:57:31). Verbatim here as `original_source.md`. Read 2026-10-15 (FMZ-C).
- Status: PORTED (batch C1). Not run.
- Near-duplicate group: **DG427120** (3 members, best partner #435898, Jaccard 0.892); ported anyway (rule 7).

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar counts and ratios of averages. |
| 3 | PASS | "CryptoBottom" is a candle rule; exchange pair in the header only. |
| 4 | DONE | 100 % of equity per trade stored in `original_sizing.txt`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG427120. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 10, 40] x `use_cb` [True, False]: **6 trials**; defaults 20 / True (the source's); colour test on.

## Ambiguities resolved

- Same-bar long and short conditions: the side not held is entered (Pine ignores a same-direction entry); from flat, long first.
- trend is na until its first state; always in the market after the first entry (REVERSAL INTENDED).
- FREQ = "15min" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_channel_breakout"`.

## Marks

`none`
