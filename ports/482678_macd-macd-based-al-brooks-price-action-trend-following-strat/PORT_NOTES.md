# #482678 MACD结合阿尔布鲁克斯价格行为的趋势跟踪策略-MACD-Based-Al-Brooks-Price-Action-Trend-Following-Strategy -> `fmz_482678_sma52_side_macd_state_neutral_exit_reversal`

- FMZ source id: 482678 (lineage).
- Source: https://www.fmz.com/strategy/482678 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-19 17:36:15). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C248). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; re-sent bracket described (pending) |
| 2 | PASS | SMA side with MACD state |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [52, 100] x `macd_fast` [12, 8]: **4 trials**; MACD slow 26, signal 9; the bracket is pending.

## Ambiguities resolved

- The re-sent 1 % / 2 % bracket is pending. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "macd"`.

## Marks

`trailing_stop_pending`
