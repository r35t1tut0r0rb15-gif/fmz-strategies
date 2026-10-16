# #427894 Moving Average Breakout Strategy -> `fmz_427894_heikin_ashi_turn_long`

- FMZ source id: 427894 (lineage).
- Source: https://www.fmz.com/strategy/427894 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-09-26 16:18:37). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C13) AS WRITTEN. Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close entries; bracket fixed at entry. |
| 2 | PASS | Candle colours and percentages. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Quantity and position cap stored; exits quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`validation` [3, 2] x `tp_pct` [1, 2] x `sl_pct` [25, 5]: **8 trials**; defaults 3 / 1 / 25 (the source's).

## Ambiguities resolved

- Heikin Ashi of the chart's own bars. `tp_stop` 0.01, `sl_stop` 0.25.
- The trail is inert as written (self-referencing trailLong; trail_price without trail_offset): not ported.
- Long only. Stop module: `portfolio_kwargs` `{}`. FREQ = "1h".

## Decision owed

Intended trail: probably 0.2 % below the highest close since entry.

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`
