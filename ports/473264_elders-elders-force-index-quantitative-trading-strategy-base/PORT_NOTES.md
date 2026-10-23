# #473264 基于标准差和移动平均线的Elders力量指数量化交易策略-Elders-Force-Index-Quantitative-Trading-Strategy-Based-on-Standard-Deviation-and-Moving-Averages -> `fmz_473264_efi_zscore_ratchet_atr_stop_target_followed`

- FMZ source id: 473264 (lineage).
- Source: https://www.fmz.com/strategy/473264 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-28 17:08:24). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V34). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; ratcheting stop and target followed in the signals |
| 2 | PASS | Elder Force Index z-score breakouts |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`numdev` [2.0, 1.5] x `tp_mult` [0.5, 1.0]: **4 trials**; EFI 13 / 50, z over 50, ATR 14 x 1.5.

## Ambiguities resolved

- Ratcheting stop / target followed at the next open after a touch. Volume = broker tick volume. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "force_index"`.

## Marks

`trailing_stop_pending`
