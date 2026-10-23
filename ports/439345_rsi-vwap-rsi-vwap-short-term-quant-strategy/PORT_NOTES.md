# #439345 基于RSI和VWAP的短线量化策略RSI-VWAP-Short-term-Quant-Strategy -> `fmz_439345_rsi17_of_session_vwap_19_80_1h_long_only`

- FMZ source id: 439345 (lineage).
- Source: https://www.fmz.com/strategy/439345 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-19 14:21:15). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V22). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI of the session VWAP leaving oversold / overbought |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [17, 14] x `over_sold` [19.0, 30.0]: **4 trials**; overbought 80.

## Ambiguities resolved

- Session VWAP at the broker day. Volume = broker tick volume (VWAP). Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "vwap_breakout"`.

## Marks

`none`
