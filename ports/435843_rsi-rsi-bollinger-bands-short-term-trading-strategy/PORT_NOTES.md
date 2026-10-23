# #435843 RSI与布林带结合的短线交易策略RSI-Bollinger-Bands-Short-term-Trading-Strategy -> `fmz_435843_rsi_volume_weighted_channel_cross_stop_flip_reversal`

- FMZ source id: 435843 (lineage).
- Source: https://www.fmz.com/strategy/435843 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-12-19 11:31:09). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V17). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-based stop as a reversal signal |
| 2 | PASS | RSI against a volume-weighted RSI channel |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`len_bb` [25, 50] x `sl` [0.94, 0.97]: **4 trials**; RSI 14, multiplier 2, ratio 0.6.

## Ambiguities resolved

- Stop flips to short, as written; na comparisons false. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_threshold"`.

## Marks

`none`
