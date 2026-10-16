# #427871 Adaptive Trading Strategy Based on Multiple EMA Crossovers -> `fmz_427871_side_ema_pairs_pct_stops`

- FMZ source id: 427871 (lineage).
- Source: https://www.fmz.com/strategy/427871 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-26 14:41:00). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C13). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; stops fixed at entry. |
| 2 | PASS | EMA lengths and percentages. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Commented strategy() sizing stored; stops quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`lttl` [144, 89] x `long_sl` [1.7, 3.4] x `short_sl` [0.4, 1]: **8 trials**; defaults 144 / 1.7 / 0.4 (the source's); the eight EMA lengths and the short trend EMA 89 fixed.

## Ambiguities resolved

- Per-side stops: `sl_stop` series from the signal bar (1.7 % long, 0.4 % short), shifted onto the fill.
- Closes on the bar of the opposite entry dropped (reversal); a long close with a same-bar long signal while long stays long (rare; stated).
- strategy() commented out; date range dropped. Stop module: `portfolio_kwargs` `{}`; REVERSAL INTENDED. Stops on 12-hour bars: mark `coarse_bar_stop`. FREQ = "12h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop`
