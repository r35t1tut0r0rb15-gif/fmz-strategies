# #425797 Trade03-双均线波动率差过滤 -> `fmz_425797_ema_range_change_filter`

- Source: https://www.fmz.com/strategy/425797 (MyLanguage, author 作手君TradeMan, FMZ last
  modified 2023-09-04 22:33:22). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A19). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | ADAPT | Additive S1 (price units) in DBL/KBL -> `s1_atr` x ATR(14). |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | LOTS formula (MONEYTOT) -> `original_sizing.txt`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`S1` [50, 100] x `s1_atr` [0.25, 0.5, 1.0] = **6 trials**. ST 1 % stays at the original.

## Ambiguities resolved

- S1 as an additive price constant in DBL/KBL -> `s1_atr` x ATR(14) (criterion 2); S1 / 10 S1 stay as lengths.
- BKPRICE/SKPRICE = BPK/SPK signal-bar close; statements in order, net change per bar emitted.
- LOTS -> original_sizing.txt. `FREQ = "1h"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks (2026-10-07)

`none`
