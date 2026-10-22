"""Parabolic SAR 0.02 / 0.02 / 0.2 on 2-hour bars with the previous broker day's SAR: a flip of the 2-hour SAR to bullish with the close also over the daily SAR goes long, the mirror goes short; the close on the wrong side of either SAR closes; reversing.
Port of FMZ strategy #488134 "多时间框架抛物线SAR动态趋势跟踪量化策略-Multi-Timeframe-Parabolic-SAR-Dynamic-Trend-Following-Quantitative-Strategy" (Multi-Timeframe Parabolic SAR Strategy ver 1.0).

FMZ source id: 488134

Source
    https://www.fmz.com/strategy/488134 (PineScript v5, FMZ last modified 2025-03-25 13:22:41).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 203-272), SAR 0.02 / 0.02 / 0.2; higher time frame "D"; both shown (on)
    trend = close > sar ? 1 : -1;  htrend = close > security("D", sar) ? 1 : -1
    trend == 1 and htrend == 1 and trend[1] == -1 -> entry Long;  mirror -> entry Short
    trend == -1 or htrend == -1 -> close Long;  trend == 1 or htrend == 1 -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "D" request has lookahead off: it is read as the last completed broker day (as #440503), the
      SAR of daily bars built from the module's own 2-hour bars. With both SARs shown (the defaults) only
      the two-frame entries apply. A short entry also meets the long exit, so it reverses (REVERSAL
      INTENDED). ta.sar follows Pine's reference implementation. No sizing code. FREQ = "2h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; daily SAR from completed broker days.
    2 generic: PASS, two-frame Parabolic SAR flips.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone) for the daily SAR.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_488134_psar_flip_daily_psar_filter_reversal"
FAMILY = "parabolic_sar"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "start": [0.02, 0.01],
    "maximum": [0.2, 0.1],
}
DEFAULT_PARAMS = {"start": 0.02, "maximum": 0.2}


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


def _sar(hv, lv, cv, start, inc, mx):
    """Pine's ta.sar as documented (pine_sar)."""
    m = len(cv)
    out = np.full(m, np.nan)
    res = mm = acc = np.nan
    below = None
    for i in range(1, m):
        first = False
        if i == 1:
            if cv[1] > cv[0]:
                below, mm, res = True, hv[1], lv[0]
            else:
                below, mm, res = False, lv[1], hv[0]
            first, acc = True, start
        res = res + acc * (mm - res)
        if below:
            if res > lv[i]:
                first, below = True, False
                res, mm, acc = max(hv[i], mm), lv[i], start
        else:
            if res < hv[i]:
                first, below = True, True
                res, mm, acc = min(lv[i], mm), hv[i], start
        if not first:
            if below:
                if hv[i] > mm:
                    mm, acc = hv[i], min(acc + inc, mx)
            else:
                if lv[i] < mm:
                    mm, acc = lv[i], min(acc + inc, mx)
        if below:
            res = min(res, lv[i - 1])
            if i > 1:
                res = min(res, lv[i - 2])
        else:
            res = max(res, hv[i - 1])
            if i > 1:
                res = max(res, hv[i - 2])
        out[i] = res
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    st, mx = float(p["start"]), float(p["maximum"])
    sar = pd.Series(_sar(h.to_numpy(dtype=float), lo.to_numpy(dtype=float), c.to_numpy(dtype=float),
                         st, st, mx), index=c.index)
    day = broker_day(c.index)
    d = pd.DataFrame({"h": h.groupby(day).max(), "l": lo.groupby(day).min(), "c": c.groupby(day).last()})
    dsar = pd.Series(_sar(d["h"].to_numpy(dtype=float), d["l"].to_numpy(dtype=float),
                          d["c"].to_numpy(dtype=float), st, st, mx), index=d.index)
    hsar = pd.Series(dsar.shift(1).reindex(day).to_numpy(), index=c.index)   # last completed day
    tr = pd.Series(np.where(c > sar, 1, -1), index=c.index)
    ht = pd.Series(np.where(c > hsar, 1, -1), index=c.index)
    le = (tr == 1) & (ht == 1) & (tr.shift(1) == -1)
    se = (tr == -1) & (ht == -1) & (tr.shift(1) == 1)
    lx = ((tr == -1) | (ht == -1)) & ~se
    sx = ((tr == 1) | (ht == 1)) & ~le
    return le, lx, se, sx


def portfolio_kwargs(**params):
    return {}
