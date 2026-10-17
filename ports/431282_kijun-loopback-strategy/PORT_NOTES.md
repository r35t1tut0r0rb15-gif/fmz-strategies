# #431282 Kijun Loopback Strategy -> `fmz_431282_kijun_loopback`

- FMZ source id: 431282 (lineage).
- Source: https://www.fmz.com/strategy/431282 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-06 16:46:45). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C44). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | ADAPT | Tick stop / point target -> ATR fractions |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The risk-based lot formula and the equity protector stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ks_len` [20, 40] x `tp_atr` [1.0, 2.0]: **4 trials**; ATR 14 and the 1.5 ATR stop fixed.

## Ambiguities resolved

- The FX tick formulas as ATR multiples (criterion 2 ADAPT); the equity protector is sizing. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks

`none`
