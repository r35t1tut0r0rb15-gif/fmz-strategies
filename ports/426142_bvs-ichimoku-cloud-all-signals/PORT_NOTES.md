# #426142 BV's ICHIMOKU CLOUD SIGNAL TESTER -> `fmz_426142_tenkan_kijun_atr_bracket`

- Source: https://www.fmz.com/strategy/426142 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-08 16:18:04). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A19). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | ADAPT | Tick distances (forex pip adjuster) -> ATR(14) multiples. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_atr` [1.0, 1.5, 2.0] x `tp_atr` [1.0, 2.0] = **6 trials**. Ichimoku 9 / 26 and the default signal stay at the originals.

## Ambiguities resolved

- Tick distances ATR x 100000 x mult = mult x ATR on 5-digit forex (evident meaning) -> sl/tp ATR multiples at the signal bar (criterion 2).
- Exit re-issued each bar with the current ATR (moving levels): `trailing_stop_pending`; port fixes the signal bar ATR.
- Year filter (year > 2017) is a backtest window: dropped. `FREQ = "1h"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks (2026-10-07)

`trailing_stop_pending`
