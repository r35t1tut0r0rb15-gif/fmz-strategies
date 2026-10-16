# #427346 Volatility Tracking Stop Loss Strategy -> `fmz_427346_hpotter_volatility_regime`

- FMZ source id: 427346 (lineage).
- Source: https://www.fmz.com/strategy/427346 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-09-20 11:31:12). Verbatim here as `original_source.md`. Read 2026-10-15 (FMZ-C).
- Status: PORTED (batch C5). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | ATR against its own average. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [10, 20] x `length_ma` [26, 13, 52]: **6 trials**; defaults 10 / 26 (the source's).

## Ambiguities resolved

- No stop exists in the code despite the title. nRes starts from 0 (nz) as written.
- REVERSAL INTENDED. FREQ = "4h" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_stop_cross"`.

## Marks

`none`
