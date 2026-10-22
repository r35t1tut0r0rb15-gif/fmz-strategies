# #440429 基于20日EMA通道的交易策略All-about-EMA-Channel-Trading-Strategy -> `fmz_440429_ema20_high_low_channel_long`

- FMZ source id: 440429 (lineage).
- Source: https://www.fmz.com/strategy/440429 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-30 15:24:07). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C134). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA channel crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_len` [20, 50]: **2 trials**.

## Ambiguities resolved

- Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_envelope_breakout"`.

## Marks

`none`
