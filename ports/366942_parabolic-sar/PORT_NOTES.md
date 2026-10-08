# #366942 Parabolic SAR (PSAR) -> `fmz_366942_psar_classic_flip`

- Source: https://www.fmz.com/strategy/366942 (PineScript v4, author ChaoZhang, FMZ last
  modified 2022-05-31 19:01:00). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A15). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar-derived quantities only. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`start` [0.01, 0.02] x `increment` [0.01, 0.02] x `maximum` [0.1, 0.2] = **8 trials**.

## Ambiguities resolved

- sar() as documented by TradingView (pine_sar).
- Same rule as #365722 with the classic defaults.
- `FREQ = "5min"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "parabolic_sar"`.

## Marks (2026-10-07)

`none`
