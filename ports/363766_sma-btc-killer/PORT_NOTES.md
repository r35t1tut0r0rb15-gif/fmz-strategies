# #363766 Sma BTC killer -> `fmz_363766_sma_adx_kama_pivot_trend`

- Source: https://www.fmz.com/strategy/363766 (PineScript v4, author ChaoZhang, FMZ last
  modified 2022-05-17 13:41:03). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A10). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar-derived quantities only. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | Inactive sizing lines (commented-out strategy() etc.) -> `original_sizing.txt`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`adx_len` [14, 29] x `adx_th` [21, 25] x `cloud_len` [11, 20] = **8 trials**. SMAs 14/28/55, pivot period 18 and ATR 5 x 6 stay at the originals.

## Ambiguities resolved

- "Last signalled side" = the author's in_longCondition (CondIni on Long_MA[1] / Short_MA[1]).
- Same-bar entry and close_all: flat when a position existed (exit only), entry from flat.
- MAMA phase/period recursion reproduced as coded, with its nz() seeds.
- `FREQ = "2h"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks (2026-10-07)

`none`
