# #482766 VWAP波动反转策略在标准差通道上的多空突破系统-VWAP-Volatility-Reversal-Strategy-with-Standard-Deviation-Channel-Breakout-System -> `fmz_482766_vwap_band_reversal_breakout_vwap_target_1h_reversal`

- FMZ source id: 482766 (lineage).
- Source: https://www.fmz.com/strategy/482766 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-20 09:33:31). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V39). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; signal-bar levels as fractions of the fill |
| 2 | PASS | VWAP-band reversal breakouts back toward the VWAP |
| 3 | PASS | Exchange pair in the header only (ETH named in the title). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`dev_len` [20, 50] x `dev_mult` [1.0, 1.5]: **4 trials**.

## Ambiguities resolved

- Stored reversal levels cleared while long. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "vwap"`.

## Marks

`none`
