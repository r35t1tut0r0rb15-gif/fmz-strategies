# #427279 基于ADX-EFI指标的趋势回调策略ADX-EFI-50-Moving-Average-Channel-Pullback-Strategy -> `fmz_427279_efi15_120_pullback_adx20_ema50_channel_atr_bracket_reversal`

- FMZ source id: 427279 (lineage).
- Source: https://www.fmz.com/strategy/427279 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-09-19 17:10:51). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V6). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; ATR bracket from the signal bar |
| 2 | PASS | Force-index pullbacks in an ADX trend |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The commented strategy() (margin 100, capital 100000) stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`efi_fast` [15, 8] x `adx_min` [20.0, 25.0]: **4 trials**; EFI slow 120, ATR 14 x 4 / 8.

## Ambiguities resolved

- Bracket fixed at the signal bar; re-sent levels not followed. Volume = broker tick volume.
- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "force_index"`.

## Marks

`trailing_stop_pending`
