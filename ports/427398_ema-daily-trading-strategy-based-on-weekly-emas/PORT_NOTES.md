# #427398 Daily Trading Strategy Based on Weekly EMAs -> `fmz_427398_weekly_emas_on_3h`

- FMZ source id: 427398 (lineage).
- Source: https://www.fmz.com/strategy/427398 (PineScript v1, author ChaoZhang, FMZ last
  modified 2023-09-20 17:11:52). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C7). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | MA lengths only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Pyramiding 100 stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [42, 21] x `mid` [84, 63] x `slow` [182, 126]: **8 trials**; defaults 42 / 84 / 182 (the source's).

## Ambiguities resolved

- The "Exit_1" / "Exit_2" orders are short entries (long = false): they reverse, as written.
- Adds (pyramiding 100) are sizing; the net side follows the last signal; on a bar with both, the short (placed last) wins.
- FREQ = "3h" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
