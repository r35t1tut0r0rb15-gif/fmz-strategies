# #436756 基于MFI和MA的量化反转策略MFI-and-MA-Based-Quantitative-Reversal-Strategy -> `fmz_436756_mfi3_extreme_body_bar_sma80_1m_reversal`

- FMZ source id: 436756 (lineage).
- Source: https://www.fmz.com/strategy/436756 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-27 14:42:16). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V19). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | MFI extreme follow-through bars with an SMA filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`mfi_len` [3, 5] x `ma_len` [80, 200]: **4 trials**; body 0.5, levels 100 / 0.

## Ambiguities resolved

- The na-on-entry bracket is not ported. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "mfi_threshold"`.

## Marks

`none`
