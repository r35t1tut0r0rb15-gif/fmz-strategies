# #427258 Aroon Indicator Based Quantitative Strategy -> `fmz_427258_noro_aroon_long`

- FMZ source id: 427258 (lineage).
- Source: https://www.fmz.com/strategy/427258 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-09-19 15:47:21). Verbatim here as `original_source.md`. Read 2026-10-15 (FMZ-C).
- Status: PORTED (batch C3). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar counts only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity stored in `original_sizing.txt`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [7, 14, 25]: **3 trials**; default 7 (the source's).

## Ambiguities resolved

- Short side off: its qty-0 entry only closes the long (Noro idiom).
- `if true -> strategy.close_all()` is read as Noro's backtest-window close with its time test replaced by `true` (FMZ conversion): dropped. Taken literally, every long would be closed one bar after it opens. **Decision owed** if that literal version is wanted (a separate module).
- highestbars / lowestbars include the current bar; ties go to the most recent bar.
- FREQ = "1h" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_breakout"`.

## Marks

`none`
