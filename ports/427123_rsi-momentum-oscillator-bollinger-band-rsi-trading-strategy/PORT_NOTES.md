# #427123 Momentum Oscillator Bollinger Band RSI Trading Strategy -> `fmz_427123_bb_rsi_long`

- FMZ source id: 427123 (lineage).
- Source: https://www.fmz.com/strategy/427123 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-18 14:07:51). Verbatim here as `original_source.md`. Read 2026-10-15 (FMZ-C).
- Status: PORTED (batch C1). Not run.
- Near-duplicate group: **DG427123** (with #444357, Jaccard 0.885); ported anyway (rule 7).

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the commented-out strategy() line leaves Pine's defaults. |
| 2 | PASS | RSI levels, a band in standard deviations, stops as fractions of price. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | TP / SL bracket ported via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG427123. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`bb_mult` [2.0, 2.5] x `tp_pct` [10, 3] x `sl_pct` [25, 5]: **8 trials**; defaults 2.0 / 10 / 25 (the source's); RSI 14 (30 / 70) and BB 20 fixed.

## Ambiguities resolved

- strategy() is commented out (pyramiding 50, calc_on_every_tick): Pine defaults apply.
- Stop module: `portfolio_kwargs` returns `{}` (driver rule D4); long only, so opposite entries cannot occur.
- FREQ = "1min" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`
