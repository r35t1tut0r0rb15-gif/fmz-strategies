# #428854 Trend Following Moving Stop Loss MA Strategy -> `fmz_428854_rsi2_dip_signal_average_exits`

- FMZ source id: 428854 (lineage).
- Source: https://www.fmz.com/strategy/428854 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-10-10 10:36:16). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C21). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-checked exits. |
| 2 | PASS | RSI levels and percentages only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The commented-out strategy() and the pyramiding counters stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG428854. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsin` [14, 10] x `tp` [33, 66] (x 0.01 %): **4 trials**; RSI 2, stop 55 (x 0.01 %) and the counts fixed.

## Ambiguities resolved

- The average uses signal closes (the script's own bookkeeping), adds included; exits on closes.
- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
