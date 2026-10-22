"""Parabolic SAR breaks with an EMA 100 offset filter, broker days: a high breaking up to the previous SAR after being under it, or an EMA 100 / 10 cross with the close above the SAR, while the close is 1 % above
the EMA 100, goes long; the mirror goes short; a high above the SAR closes a short, a low under it closes a long.
Port of FMZ strategy #439202 "抛物线SAR趋势追踪策略Parabolic-SAR-Trend-Tracking-Strategy" (SAR Trend Trader Strategy).

FMZ source id: 439202

Source
    https://www.fmz.com/strategy/439202 (PineScript v3, FMZ last modified 2024-01-18 12:21:17).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 151-214), EMA 100 / 10, offset 1 %; SAR 0.01 / 0.005 / 0.08; date window true
    long = (high[1] < sar[2] and high >= sar[1] and close > ema + 1 %) or (crossunder(ema 100, ema 10) and close > sar and close > ema + 1 %);  short mirror
    high > sar -> close Short;  low < sar -> close Long;  long -> entry Long;  short -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The closes come first and act on the position held at the bar close; an entry is taken when not
      already on that side at the bar close (a same-side entry on a bar that also closes that side is
      ignored, so the bar ends flat). The SAR follows Pine's ta.sar. time_cond is true. strategy.entry
      reverses: REVERSAL INTENDED. The 100 % of equity size is sizing. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SAR breaks and EMA filters.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_439202_sar_trend_trader_ema_offset"
FAMILY = "volatility_stop_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "slow": [100, 50],
    "offset": [1.0, 0.5],
}
DEFAULT_PARAMS = {"slow": 100, "offset": 1.0, "fast": 10, "start": 0.01, "increment": 0.005, "maximum": 0.08}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


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
    sar = pd.Series(_sar(h.to_numpy(dtype=float), lo.to_numpy(dtype=float), c.to_numpy(dtype=float),
                         float(p["start"]), float(p["increment"]), float(p["maximum"])), index=c.index)
    ema = c.ewm(span=int(p["slow"]), adjust=False).mean()
    fe = c.ewm(span=int(p["fast"]), adjust=False).mean()
    off = float(p["offset"]) / 100 * ema
    xu = (ema < fe) & (ema.shift(1) >= fe.shift(1))
    xo = (ema > fe) & (ema.shift(1) <= fe.shift(1))
    long_ = (((h.shift(1) < sar.shift(2)) & (h >= sar.shift(1)) & (c > ema + off))
             | (xu & (c > sar) & (c > ema + off))).to_numpy()
    short_ = (((lo.shift(1) > sar.shift(2)) & (lo <= sar.shift(1)) & (c < ema - off))
              | (xo & (c < sar) & (c < ema - off))).to_numpy()
    cs, cl = (h > sar).to_numpy(), (lo < sar).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        new = pos
        if pos == -1 and cs[i]:
            new = 0
        if pos == 1 and cl[i]:
            new = 0
        if long_[i] and pos != 1:
            new = 1
        elif short_[i] and pos != -1:
            new = -1
        pos = new
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), pd.Series((prev == 1) & (tgt == 0), index=ix),
            pd.Series((tgt == -1) & (prev != -1), index=ix), pd.Series((prev == -1) & (tgt == 0), index=ix))


def portfolio_kwargs(**params):
    return {}
