# #434555 Johns Bitcoin Intraday Trading Strategy Based on Multiple Indicators -> `fmz_434555_stochrsi_macd_mfi_oversold_1m_long`

- FMZ source id: 434555 (lineage).
- Source: https://www.fmz.com/strategy/434555 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-07 15:23:44). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V15). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Stochastic-RSI, MACD and MFI oversold entries |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Strategy(): 10000 cash per trade, capital 10000, pyramiding 1, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`mfi_buy` [23, 30] x `os_level` [34, 20]: **4 trials**; stochastic RSI 14 / 14 / 3 / 2, MACD 12 / 26 / 9, MFI exit 80.

## Ambiguities resolved

- The na-on-entry stop is not ported. SELL = exit (allow_entry_in long). Volume = broker tick volume. Long only. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "stochastic_rsi"`.

## Marks

`none`
