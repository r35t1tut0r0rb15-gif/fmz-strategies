# #451029 Automated Trading Strategy Based on RSI Overbought and Oversold Levels -> `fmz_451029_rsi_extreme_one_hour_timer_reversal`

- FMZ source id: 451029 (lineage).
- Source: https://www.fmz.com/strategy/451029 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-05-11 11:57:20). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C183). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the timer is a close-time test |
| 2 | PASS | RSI extremes with a time exit |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_len` [14, 7] x `exit_minutes` [60, 240]: **4 trials**; the levels fixed.

## Ambiguities resolved

- Timer restarted by every signal. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
