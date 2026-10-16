# #428056 Hammer and Shooting Star Pattern Trading Strategy -> `fmz_428056_hammers_and_stars`

- FMZ source id: 428056 (lineage).
- Source: https://www.fmz.com/strategy/428056 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-28 11:11:35). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C15). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry. |
| 2 | PASS | Candle ratios and ATR multiples. |
| 3 | PASS | The BTC_USDT security only feeds the off sizing. |
| 4 | DONE | Risk sizing and alert settings stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`stop_mult` [1, 2] x `rr` [1, 2] x `fib` [0.333, 0.5]: **8 trials**; defaults 1 / 1 / 0.333 (the source's); ATR 14 and the 3-ATR size filter fixed.

## Ambiguities resolved

- Levels as fractions of the signal close, re-based on the fill (house convention).
- "Flat" follows the house bracket. Alerts / conversion security / position size are sizing.
- Stop module: `portfolio_kwargs` `{}`; entries only from flat. Stops on 2-hour bars: mark `coarse_bar_stop`. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`coarse_bar_stop`
