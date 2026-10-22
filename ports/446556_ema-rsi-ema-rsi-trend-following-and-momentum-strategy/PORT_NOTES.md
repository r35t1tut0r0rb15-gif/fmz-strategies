# #446556 EMA-RSI-趋势追踪与动量策略-EMA-RSI-Trend-Following-and-Momentum-Strategy -> `fmz_446556_rsi5_dip_spike_ema90_300_reversal`

- FMZ source id: 446556 (lineage).
- Source: https://www.fmz.com/strategy/446556 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-03-29 16:30:42). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C176). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI extremes with an EMA trend order |
| 3 | PASS | Exchange pair in the header only; the Bybit level is display only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [90, 50] x `rsi_lower` [45, 30]: **4 trials**; the slow EMA, the RSI length and the upper level fixed.

## Ambiguities resolved

- No exit sent. REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
