# #437010 RSI菲波那契回调策略RSI-Fibonacci-Retracement-Strategy -> `fmz_437010_rsi_hl2_fib_level_state`

- FMZ source id: 437010 (lineage).
- Source: https://www.fmz.com/strategy/437010 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-29 14:51:43). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C98). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI level |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size and commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 21] x `fib_level` [38.2, 50.0]: **4 trials**.

## Ambiguities resolved

- Unused backtest range dropped; always in the market. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
