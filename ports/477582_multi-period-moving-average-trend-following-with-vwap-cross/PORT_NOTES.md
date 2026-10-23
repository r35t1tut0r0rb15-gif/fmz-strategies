# #477582 Multi Period Moving Average Trend Following with VWAP Cross Strategy -> `fmz_477582_sma9_50_cross_sma200_session_vwap_2h_reversal`

- FMZ source id: 477582 (lineage).
- Source: https://www.fmz.com/strategy/477582 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-01-06 15:30:00). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V36). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMA 9 / 50 crossings in the SMA 200 trend with a session-VWAP filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [9, 20] x `slow` [50, 100]: **4 trials**; SMA 200, session VWAP.

## Ambiguities resolved

- Session VWAP reset on the broker day. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
