# #427386 Multi-timeframe Trading Strategy with Bollinger Bands -> `fmz_427386_underworld_hunter_bands`

- FMZ source id: 427386 (lineage).
- Source: https://www.fmz.com/strategy/427386 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-20 15:47:46). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C6). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bands in standard deviations. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Order size floor(50000 / close) stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [75, 40, 150] x `mult` [1.9, 2.5]: **6 trials**; defaults 75 / 1.9 (the source's).

## Ambiguities resolved

- basis: the SMA on its first valid bar, the nested triple EMA afterwards (as written).
- The mean-reversion "Sneak" branch is off by default: not ported. The CCI only colours bars; "multi-timeframe" is only in the title.
- Entries only from flat; an exit is taken before an entry on the same bar. Broker-day bars. FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_breakout"`.

## Marks

`none`
