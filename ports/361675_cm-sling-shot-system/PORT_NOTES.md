# #361675 CM-Sling-Shot-System -> `fmz_361675_slingshot_faded`

- Source: https://www.fmz.com/strategy/361675 (PineScript, ChrisMoody's CM_SlingShotSystem with
  orders added; FMZ last modified 2022-05-07 17:06:50). Verbatim here as `original_source.md`.
  Read 2026-10-07 (worker A).
- Status: PORTED (batch A4). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Pine bar-close evaluation, next-open fills. |
| 2 | PASS | EMA relations only. |
| 3 | PASS | Binance futures pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED | |

## Declared grid (criterion 5)

`ema_fast` [20, 38, 50] x `ema_slow` [62, 100] = **6 trials**.

## Ambiguities resolved

- **Direction as written**: the orders fade ChrisMoody's signals (SELL on the up-trend re-entry,
  BUY on the down-trend one). Ported as written; flagged in the worker report.
- `FREQ = "15min"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend_oscillator_pullback"`.

## Marks (2026-10-07)

`none`
