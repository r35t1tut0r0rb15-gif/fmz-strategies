"""Parabolic SAR flips agreeing with the daily SAR side, 2-hour bars: a bar whose close flips above its own SAR while the
close is also above the last completed broker day's SAR goes long; the mirror goes short; a long closes when the close
is below either SAR (shorts mirrored).
Port of FMZ strategy #488134 "多时间框架抛物线SAR动态趋势跟踪量化策略-Multi-Timeframe-Parabolic-SAR-Dynamic-Trend-Following-Quantitative-Strategy" (Multi-Timeframe Parabolic SAR Strategy ver 1.0).

FMZ source id: 488134

Source
    https://www.fmz.com/strategy/488134 (PineScript v5, FMZ last modified 2025-03-25 13:22:41).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 209-271), SAR 0.02 / 0.02 / 0.2 on the chart and on "D"
    currentTrend = close > sar ? 1 : -1;  higherTrend = close > request.security("D", sar, lookahead_off) ? 1 : -1
    long = currentTrend == 1 and higherTrend == 1 and currentTrend[1] == -1 -> entry long (short mirrored)
    currentTrend == -1 or higherTrend == -1 -> close long;  currentTrend == 1 or higherTrend == 1 -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The daily SAR is the last completed broker day's (house rule for a higher timeframe, as #430771): daily highs /
      lows / closes from the port's bars grouped by broker day, the SAR on them, shifted one day.
    * The show-inputs default to both on, so only the two-timeframe rule applies.
    * Closes act on the position held at the bar's start and never undo an entry on that bar (#430850); a short signal
      while long reverses. REVERSAL INTENDED.
    * FREQ = "2h" from the backtest header. No stops.

Admission criteria
    1 fits the interface: PASS, bar-close orders; completed daily values.
    2 generic: PASS, SAR.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone) for the daily SAR; no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_488134_sar_flip_daily_sar_agree"
FAMILY = "parabolic_sar"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "sar_max": [0.2, 0.1],
    "sar_inc": [0.02, 0.01],
}
DEFAULT_PARAMS = {"sar_start": 0.02, "sar_inc": 0.02, "sar_max": 0.2}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def _sar_pine(bars, start, inc, maximum):
    """ta.sar as TradingView documents it (pine_sar), as #428699."""
    h, lo, c = (bars[k].to_numpy(dtype=float) for k in ("high", "low", "close"))
    m = len(c)
    out = np.full(m, np.nan)
    result = max_min = acc = np.nan
    below = False
    for i in range(1, m):
        first = False
        if i == 1:
            if c[1] > c[0]:
                below, max_min, result = True, h[1], lo[0]
            else:
                below, max_min, result = False, lo[1], h[0]
            first, acc = True, start
        result = result + acc * (max_min - result)
        if below:
            if result > lo[i]:
                first, below = True, False
                result, max_min, acc = max(h[i], max_min), lo[i], start
        else:
            if result < h[i]:
                first, below = True, True
                result, max_min, acc = min(lo[i], max_min), h[i], start
        if not first:
            if below and h[i] > max_min:
                max_min, acc = h[i], min(acc + inc, maximum)
            elif (not below) and lo[i] < max_min:
                max_min, acc = lo[i], min(acc + inc, maximum)
        if below:
            result = min(result, lo[i - 1])
            if i > 1:
                result = min(result, lo[i - 2])
        else:
            result = max(result, h[i - 1])
            if i > 1:
                result = max(result, h[i - 2])
        out[i] = result
    return pd.Series(out, index=bars.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    cur = _sar_pine(bars_df, p["sar_start"], p["sar_inc"], p["sar_max"])
    lab = broker_day(bars_df.index)
    day = pd.DataFrame({"high": h.to_numpy(), "low": lo.to_numpy(), "close": c.to_numpy()}, index=lab)
    d = day.groupby(level=0).agg({"high": "max", "low": "min", "close": "last"})
    dsar = _sar_pine(d, p["sar_start"], p["sar_inc"], p["sar_max"]).shift(1)   # the last completed broker day
    hsar = dsar.reindex(lab).to_numpy()
    cv = c.to_numpy(dtype=float)
    ct = np.where(cv > cur.to_numpy(), 1, -1)
    ht = np.where(cv > hsar, 1, -1)
    ct1 = np.concatenate(([0], ct[:-1]))
    go_l = (ct == 1) & (ht == 1) & (ct1 == -1)
    go_s = (ct == -1) & (ht == -1) & (ct1 == 1)
    out_l = (ct == -1) | (ht == -1)
    out_s = (ct == 1) | (ht == 1)
    m = len(cv)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos = 0
    for i in range(m):
        start = pos
        if go_l[i]:
            pos = 1
        if go_s[i]:
            pos = -1
        if out_l[i] and start == 1 and pos == 1:
            pos = 0
        if out_s[i] and start == -1 and pos == -1:
            pos = 0
        if pos != start:
            le[i] = pos == 1
            se[i] = pos == -1
            lx[i] = start == 1 and pos == 0
            sx[i] = start == -1 and pos == 0
    idx = bars_df.index
    return tuple(pd.Series(x, index=idx) for x in (le, lx, se, sx))


def portfolio_kwargs(**params):
    return {}
