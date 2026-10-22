# #439241 Bottom Fishing Strategy -> `fmz_439241_coinrule_rsi_dip_under_sma_long`

- FMZ source id: 439241 (lineage).
- Source: https://www.fmz.com/strategy/439241 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-18 15:44:10). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C118). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI levels and an SMA filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size and the commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_entry` [35, 30] x `ma_len` [100, 200]: **4 trials**; RSI 14 and the close level 65 fixed.

## Ambiguities resolved

- Long only. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
