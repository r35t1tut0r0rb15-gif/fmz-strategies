# #363564 Welcome to the BEARMARKET 30MIN -> `fmz_363564_pivot_atr_trend_vwap_rsi_short_pct6_stop`

- FMZ source id: 363564 (lineage).
- Source: https://www.fmz.com/strategy/363564 (PineScript v4, author ChaoZhang, FMZ last
  modified 2022-05-16 15:52:51). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V2). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; 6 % stop from the fill |
| 2 | PASS | Trend-band / VWAP-RSI short entries with trend exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code (the commented strategy() line: fixed 1, capital 10000). |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`factor` [10.0, 5.0] x `stoploss` [6.0, 3.0]: **4 trials**; pivots 2, ATR 14, cloud 2, ADX 17 / 14, RSI 51 and VWAP RSI 22.

## Ambiguities resolved

- Precedence as written; VWAP anchored at the broker day. Volume = broker tick volume. Short only. FREQ = "30min".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`
