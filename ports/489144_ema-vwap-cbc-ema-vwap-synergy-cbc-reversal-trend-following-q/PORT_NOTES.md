# #489144 EMA-VWAP协同CBC反转趋势跟踪量化交易策略-EMA-VWAP-Synergy-CBC-Reversal-Trend-Following-Quantitative-Trading-Strategy -> `fmz_489144_cbc_flip_ema9_20_session_vwap_flip_exit_1h`

- FMZ source id: 489144 (lineage).
- Source: https://www.fmz.com/strategy/489144 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-04-02 10:31:49). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V46). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Close-beyond-previous-bar flips in the EMA and VWAP trend |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [9, 5] x `middle` [20, 30]: **4 trials**; session VWAP of close, CBC flip as written.

## Ambiguities resolved

- Flat-only entries, opposite-flip closes. Volume = broker tick volume (VWAP). FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "breakout"`.

## Marks

`none`
