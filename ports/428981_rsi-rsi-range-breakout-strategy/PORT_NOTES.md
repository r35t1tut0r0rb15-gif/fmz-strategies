# #428981 RSI区间突破策略RSI-Range-Breakout-Strategy -> `fmz_428981_smoothed_rsi3_dip_long`

- FMZ source id: 428981 (lineage).
- Source: https://www.fmz.com/strategy/428981 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-11 15:54:11). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C22). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry (re-placement pending). |
| 2 | ADAPT | The tick target -> an ATR multiple; the stop is a percentage. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The commented-out strategy() stored; the exits quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`thresh_low` [35, 25] x `tp_atr` [0.2, 1.0]: **4 trials**; RSI 3, smoothing 3 / 5, 80 and stop 2.6 % fixed.

## Ambiguities resolved

- Pending (not emitted): on each later long signal while long, the source moves the stop to 2.6 % under
  that bar's close (same exit id, so the new level replaces the old one).
- Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`trailing_stop_pending`
