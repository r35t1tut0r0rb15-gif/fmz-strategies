# #435020 动态上升ADX趋势跟踪策略Dynamic-Rising-ADX-Trend-Following-Strategy -> `fmz_435020_rising_adx_ema_side`

- FMZ source id: 435020 (lineage).
- Source: https://www.fmz.com/strategy/435020 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-11 17:18:32). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C73). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | ADX turns and an average side |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`threshold` [10, 20] x `ma_len` [20, 50]: **4 trials**; ADX 14 / 14 fixed.

## Ambiguities resolved

- Asymmetric reversal as written (position_size < 1). Same-bar entry beats the close. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "directional_movement"`.

## Marks

`none`
