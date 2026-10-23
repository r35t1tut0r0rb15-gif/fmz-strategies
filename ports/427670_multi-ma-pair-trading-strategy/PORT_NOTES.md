# #427670 Multi MA Pair Trading Strategy -> `fmz_427670_sma_ema_pullback_two_entries_bar_and_profit_count_exit_long`

- FMZ source id: 427670 (lineage).
- Source: https://www.fmz.com/strategy/427670 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-09-23 15:16:50). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V7). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bar-count and profit-count exits |
| 2 | PASS | Short-term pullback entries with time / profit-count exits |
| 3 | PASS | No exchange header. |
| 4 | DONE | Quantity 1 stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`max_bars` [10, 20] x `max_profit_closes` [5, 3]: **4 trials**; SMA 3 / 8 / 10, EMA 5 / 3.

## Ambiguities resolved

- No header: bar size pending. Volume = broker tick volume. Long only. FREQ = "bar_size_pending".

## FAMILY (proposed, user to confirm)

`FAMILY = "pullback"`.

## Marks

`bar_size_pending`
