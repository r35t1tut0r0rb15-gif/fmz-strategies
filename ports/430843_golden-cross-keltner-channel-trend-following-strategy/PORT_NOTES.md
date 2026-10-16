# #430843 Golden Cross Keltner Channel Trend Following Strategy -> `fmz_430843_keltner_golden_cross`

- FMZ source id: 430843 (lineage).
- Source: https://www.fmz.com/strategy/430843 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-11-02 14:31:10). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C40). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-checked exits. |
| 2 | PASS | Keltner channels and moving averages. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The commented-out 10 % of equity stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [21, 50] x `profit_mult` [4.0, 2.0]: **4 trials**; entry 1 / exit -1 ATR and EMA 50 / 200 fixed.

## Ambiguities resolved

- Close-checked exits; a close acts on the start position unless reversed. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_channel_breakout"`.

## Marks

`none`
