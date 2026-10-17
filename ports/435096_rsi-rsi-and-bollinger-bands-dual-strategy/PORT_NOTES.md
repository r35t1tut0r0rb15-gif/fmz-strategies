# #435096 RSI与布林带双重策略RSI-and-Bollinger-Bands-Dual-Strategy -> `fmz_435096_rsi_bb_reentry`

- FMZ source id: 435096 (lineage).
- Source: https://www.fmz.com/strategy/435096 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-12 11:53:49). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C73). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI and band crosses |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The equity-sized quantity, pyramiding and commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`bb_len` [100, 50] x `l_os` [45, 30]: **4 trials**; RSI 7 / 14, the short level 65 and 2.1 deviations fixed.

## Ambiguities resolved

- Adds not ported; same-bar entry beats the close. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`
