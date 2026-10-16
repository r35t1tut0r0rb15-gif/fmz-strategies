# #427369 Zero-Lag EMA Trend Following Strategy -> `fmz_427369_mp_zero_lag_ema`

- FMZ source id: 427369 (lineage).
- Source: https://www.fmz.com/strategy/427369 (PineScript v3, author ChaoZhang, FMZ last modified 2023-09-20 14:30:03). Verbatim here as
  `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C6). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the take-profit is a close test. |
| 2 | PASS | MA lengths, percent target. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity, commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [8, 5] x `slow` [21, 50] x `tp_pct` [3, 1.5]: **8 trials**; defaults 8 / 21 / 3 (the source's).

## Ambiguities resolved

- The template's section counters (pyramiding gate 1) leave every alternating cross as a signal.
- Take-profit measured from the signal bar's close, tested on closes (rule 3). Trailing stop and stop loss are off by default: not ported.
- The window to year 77777777 is the author's backtest window. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
