# #426847 ATR Stop Loss Ichimoku Kijun Breakout Strategy -> `fmz_426847_kijun_wpr_atr_bracket`

- Source: https://www.fmz.com/strategy/426847 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-14 20:06:11). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A26). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | ADAPT | Tick distances -> ATR(14) multiples at the signal bar. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ks_period` [20, 26] x `sl_atr` [1.5, 2.0] x `tp_atr` [0.25, 1.0, 2.0]: **12 trials**, defaults 20 / 1.5 / 0.25 (the source's 1.5 ATR; 150 points converted, 0.25 the smallest step).

## Ambiguities resolved

- Criterion 2 (ADAPT): ATR x 100000 x 1.5 ticks = 1.5 ATR on 5-digit forex (as #426142); 150-point target -> tp_atr x ATR(14); both at the signal bar.
- Loss re-issued every bar with the current ATR: trailing_stop_pending; port fixes the signal bar's ATR.
- Equity protector (open loss > 30 % of balance) is a balance check: sizing.
- Entries need flat: simulate() mirrors stop and target; Kijun exits are close-based signals.
- FREQ = "15min" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks (2026-10-07)

`trailing_stop_pending`
