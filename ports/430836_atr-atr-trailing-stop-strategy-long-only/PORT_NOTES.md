# #430836 基于ATR的跟踪止损策略仅做多ATR-Trailing-Stop-Strategy-Long-Only -> `fmz_430836_atr_two_trails_long`

- FMZ source id: 430836 (lineage).
- Source: https://www.fmz.com/strategy/430836 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-02 14:05:22). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C39). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the trail is a house trail (approximation stated). |
| 2 | PASS | ATR lines. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`af2` [3.0, 2.0] x `ap2` [10, 20]: **4 trials**; fast 5 / 0.5 fixed.

## Ambiguities resolved

- Slow-line stop as a house volatility trail on closes (approximation). Long only. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_stop_cross"`.

## Marks

`trailing_stop`
