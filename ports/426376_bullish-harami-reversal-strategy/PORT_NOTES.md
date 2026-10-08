# #426376 Bullish Harami Reversal Strategy -> `fmz_426376_bullish_harami`

- Source: https://www.fmz.com/strategy/426376 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-09-11 16:26:57). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A21). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | ADAPT | Price distances -> ATR(14) multiples at the signal bar. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_atr` [0.25, 0.5, 1.0]: **3 trials**, target 60 / 18 of the stop (the source's ratio), min body 0 ATR. Default 0.25 is the smallest step (the source's 18 USDT is a small fraction of a daily ATR).

## Ambiguities resolved

- Stop / target clear the stored price on the bar close; close_all follows on the next bar: close-based exits, tested on the harami bar too (as written).
- Criterion 2 (ADAPT): SL / TP -> ATR(14) at the harami bar; min body -> ATR on the bar (0).
- Long only.
- Daily bars are broker days.

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks (2026-10-07)

`none`
