# #445786 Flawless-Victory-DCA-动量与波动率策略Flawless-Victory-DCA-Momentum-and-Volatility-Strategy -> `fmz_445786_lower_band_rsi_guard_long_entries`

- FMZ source id: 445786 (lineage).
- Source: https://www.fmz.com/strategy/445786 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-03-22 10:54:40). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C172). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the late-armed bracket not ported (mark) |
| 2 | PASS | Lower-band closes with an RSI guard |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The 100 % of equity size stored; the percent bracket quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 50] x `rsi_lower` [42, 30]: **4 trials**; the multiplier fixed.

## Ambiguities resolved

- Bracket armed only by the exit condition: not ported (trailing_stop_pending); no exit. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`trailing_stop_pending`
