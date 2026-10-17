# #430872 Two Stage Breakout Strategy -> `fmz_430872_two_stage_open_fade`

- FMZ source id: 430872 (lineage).
- Source: https://www.fmz.com/strategy/430872 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-11-02 15:58:29). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C41). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | ADAPT | Tick stop / target -> ATR fractions |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_atr` [0.1, 1.0] x `tp_atr` [0.2, 2.0]: **4 trials**; triggers 0.25 % / 0.35 %, ATR 14 and the 02:00 UTC reference fixed.

## Ambiguities resolved

- The tick bracket as ATR fractions of the signal bar (criterion 2 ADAPT).
- The second-stage orders net to the held side; no signal, the first bracket kept.
- The 02:00 reference in UTC (Binance exchange time). REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "stop_and_reverse_bracket"`.

## Marks

`none`
