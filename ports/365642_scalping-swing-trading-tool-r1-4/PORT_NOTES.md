# #365642 Scalping Swing Trading Tool R1-6 by JustUncleL -> `fmz_365642_pac_break_ema_filter`

- Source: https://www.fmz.com/strategy/365642 (PineScript v2/v3, author ChaoZhang, FMZ last
  modified 2022-05-25 15:58:26). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A13). Not run.

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

`pac_len` [10, 20, 34] x `ema_medium` [180, 200] = **6 trials**.

## Ambiguities resolved

- Intraday chart -> medium EMA 180 (200 on daily).
- Fractals, pivots and ribbons only draw.
- `FREQ = "2h"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_envelope_breakout"`.

## Marks (2026-10-07)

`none`
