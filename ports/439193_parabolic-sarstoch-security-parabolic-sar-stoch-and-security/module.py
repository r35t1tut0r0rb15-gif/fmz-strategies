"""Parabolic SAR, stochastic and 3-hour candle filters, broker days: the SAR above the close with the stochastic K under 20 and the day's last 3-hour bar turning green (close crossing over its open) goes long;
the SAR below the close with K over 80 and that bar turning red goes short; reversing.
Port of FMZ strategy #439193 "基于Parabolic-SARStoch和Security指标的多时间框架量化交易策略Parabolic-SAR-Stoch-and-Security-Indicator-Based-Multi-Timeframe-Quantitative-Trading-Strategy" (kyenji90).

FMZ source id: 439193

Source
    https://www.fmz.com/strategy/439193 (PineScript v5, FMZ last modified 2024-01-18 11:40:38).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 133-164), SAR 0.01 / 0.01 / 0.2; stochastic 14, D 3, smooth 3; security period 180 (on a 1-day chart)
    longPSAR = sar > close;  longStoch = k < 20;  longSec = crossover(security("180", close), security("180", open));  all three -> entry Long;  the mirrors -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The 3-hour close and open requested from a daily chart are the day's LAST 3-hour bar (as #436765),
      counted from the broker day's start (17:00 America/New_York), eight per day; the crossover compares
      them across days. The SAR test is as written (long while the SAR is above the close). The SAR
      follows Pine's ta.sar. strategy.entry reverses: REVERSAL INTENDED. No sizing code. Daily bars are
      broker days, stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SAR side, stochastic levels and the last 3-hour bar's colour.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_439193_psar_stoch_last_3h_bar"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "period_k": [14, 9],
    "sar_max": [0.2, 0.1],
}
DEFAULT_PARAMS = {"period_k": 14, "sar_max": 0.2, "sar_start": 0.01, "sar_inc": 0.01, "period_d": 3,
                  "smooth_k": 3, "sec_minutes": 180}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    p = {**DEFAULT_PARAMS, **params}
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    # 3-hour bars counted from each broker day's start (17:00 America/New_York)
    ny = df.index.tz_convert("America/New_York") + pd.Timedelta(hours=7)
    mos = (ny - ny.normalize()) // pd.Timedelta(minutes=int(p["sec_minutes"]))
    b3 = df.groupby([lab, np.asarray(mos)]).agg({"open": "first", "close": "last"})
    day = b3.index.get_level_values(0)
    b3 = b3[~day.duplicated(keep="last")]                # the day's last 3-hour bar
    b3.index = b3.index.get_level_values(0)
    bars = bars.join(b3.rename(columns={"open": "sec_open", "close": "sec_close"}))
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
    sar = _sar(h.to_numpy(dtype=float), lo.to_numpy(dtype=float), c.to_numpy(dtype=float),
               float(p["sar_start"]), float(p["sar_inc"]), float(p["sar_max"]))
    n = int(p["period_k"])
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    with np.errstate(divide="ignore", invalid="ignore"):
        st = 100.0 * (c - ll) / (hh - ll).where(hh > ll)
    k = st.rolling(int(p["smooth_k"])).mean().to_numpy()
    sc, so = bars_df["sec_close"], bars_df["sec_open"]
    sec_up = ((sc > so) & (sc.shift(1) <= so.shift(1))).to_numpy()
    sec_dn = ((sc < so) & (sc.shift(1) >= so.shift(1))).to_numpy()
    cv = c.to_numpy(dtype=float)
    up = sec_up & (sar > cv) & (k < 20)
    dn = sec_dn & (sar < cv) & (k > 80)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(up, index=ix), false, pd.Series(dn, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
