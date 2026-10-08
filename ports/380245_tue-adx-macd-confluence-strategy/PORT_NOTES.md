# #380245 TUE ADX/MACD Confluence Strategy V1.0 -> `fmz_380245_dmi_macd_session_stop`

- Source: https://www.fmz.com/strategy/380245 (PineScript v5, author Zer3192, FMZ last
  modified 2022-08-27 16:37:33). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A17). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | ADAPT | Stop 1.0 price units -> `stop_atr` x ATR(14). |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`di_len` [10, 14] x `stop_atr` [0.5, 1.0, 2.0] = **6 trials**. ADX smoothing 10, MACD 12/26/9 and the session stay at the originals.

## Ambiguities resolved

- Session filter (Mon-Fri 09:30-16:00 New York, bar open time) kept as logic; it gates entries only.
- Stop 1.0 (price units) -> `stop_atr` x ATR(14) at the signal bar (criterion 2); on BTC the source stop is about 0 ATR.
- State-end closes are close-based exit signals; stops on 4 h bars: `coarse_bar_stop`.
- `FREQ = "4h"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "directional_movement"`.

## Marks (2026-10-07)

`coarse_bar_stop`
