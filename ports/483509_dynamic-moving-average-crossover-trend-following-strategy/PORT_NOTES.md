# #483509 动态均线交叉趋势跟踪组合策略-Dynamic-Moving-Average-Crossover-Trend-Following-Strategy -> `fmz_483509_ema13_21_sma120_flat_bracket_lock`

- FMZ source id: 483509 (lineage).
- Source: https://www.fmz.com/strategy/483509 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-24 09:46:10). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L18). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the re-placed bracket acts as a next-open exit. |
| 2 | PASS | Moving averages and distances relative to price. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity quoted; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sma_len` [120, 240] x `lock_pct` [0.8, 1.6]: **4 trials**; defaults 120 / 0.8 (the source's); EMA 13 / 21, the 0.2 %
minimum stop and the 5 R target fixed.

## The 0.8 % re-placement

Once the long's high reaches the signal close x 1.008, the exit is re-placed with stop = highest high x 0.997 (above
the entry) and limit = entry x (1 + 5 x newPerc) where newPerc = (entry - stop) / entry is negative: the limit lies
below the market and fills at the next open. Ported as an exit signal on that bar (rule 3); no moving level remains,
so no trailing mark.

## Ambiguities resolved

- Entries only from flat: `simulate()` mirrors the house bracket from the fill bar (as #430254 `_run`); an entry is
  allowed on the bar a stop is hit and on the bar after an exit signal. A long and a short condition on one bar: the
  long is taken. Opposite entries cannot occur.
- Stop module: `portfolio_kwargs` {} (D4). FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
