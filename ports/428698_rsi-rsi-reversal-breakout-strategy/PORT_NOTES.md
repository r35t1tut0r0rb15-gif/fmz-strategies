# #428698 RSI反转突破策略RSI-Reversal-Breakout-Strategy -> `fmz_428698_rsi2_dip_above_ema200`

- FMZ source id: 428698 (lineage).
- Source: https://www.fmz.com/strategy/428698 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-08 14:16:57). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C19). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | RSI level and price comparisons only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The commented-out strategy() line and the quantity input stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_min` [25, 10, 5] x `ema_length` [200, 100]: **6 trials**; RSI 2 and the high two bars back fixed.

## Ambiguities resolved

- Same-bar buy and sell net to nothing (no position). Rules only above the EMA, as written.
- Long only. FREQ = "2D" (blocks of 2 broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
