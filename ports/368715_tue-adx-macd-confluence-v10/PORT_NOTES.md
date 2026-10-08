# #368715 TUE ADX/MACD Confluence V1.0 -> `fmz_368715_dmi_macd_confluence`

- Source: https://www.fmz.com/strategy/368715 (PineScript v5, author Zer3192, FMZ last
  modified 2022-06-12 14:01:56). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A16). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar-derived quantities only. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | Group `ND368715` (Jaccard 0.65-0.80) with #435252 (PORT_CANDIDATE); best Jaccard 0.679 with #435252. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`di_len` [10, 14, 20] x `macd_fast` [8, 12] = **6 trials**. ADX smoothing 10 and MACD 26/9 stay at the originals.

## Ambiguities resolved

- `trade` is re-declared 0 each bar, so trade = longcheck ? 1 : shortcheck ? -1 : trade[1].
- DI as ta.dmi (RMA, fixnan).
- `FREQ = "4h"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "directional_movement"`.

## Marks (2026-10-07)

`none`
