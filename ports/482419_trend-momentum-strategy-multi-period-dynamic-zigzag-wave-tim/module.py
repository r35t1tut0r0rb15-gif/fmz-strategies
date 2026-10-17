"""Williams %R crossing up through -80 after the last significant pivot was a low goes long, crossing down through
-20 after a pivot high goes short, with a 1 % stop and a 2 % target, two-day bars.
Port of FMZ strategy #482419 "趋势动量策略-之字形多重周期动态波段择时系统-Trend-Momentum-Strategy-Multi-Period-Dynamic-ZigZag-Wave-Timing-System" (Zig Zag + Williams %R Strategy).

FMZ source id: 482419

Source
    https://www.fmz.com/strategy/482419 (PineScript v6, FMZ last modified 2025-02-18 13:29:06).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 104-205), pivots 5 / 5, deviation 1 %, %R 14 (-20 / -80), SL 1 %, TP 2 %
    pivot high confirmed and dir != -1 and (no last high or high[5] > last high x 1.01) -> last high, dir := -1
    pivot low confirmed and dir != 1 and (no last low or low[5] < last low x 0.99) -> last low, dir := 1
    dir == 1 and crossover(%R, -80) -> entry long with exit(stop = close x 0.99, limit = close x 1.02)
    dir == -1 and crossunder(%R, -20) -> entry short (mirrored)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Pivots are strict on both sides (as #430850), confirmed 5 bars later; the deviation test is as written.
    * The bracket is placed with the entry: 1 % / 2 % of the signal close, re-based on the fill (house rule).
    * Entries reverse (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (D4). Two-day bars are blocks of
      broker-day dates from 1970-01-01 (decision owed, as #426509); FREQ = "2D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders and a bracket set at entry.
    2 generic: PASS, confirmed pivots, Williams %R and percentages.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 300 % of equity; the bracket via stops(), quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone) in two-day blocks; no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_482419_zigzag_dir_williams_r_cross_pct_bracket_2d"
FAMILY = "mean_reversion"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "2D"  # backtest header period: 2d (blocks of broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "depth": [5, 3],
    "tp_pct": [2.0, 4.0],
}
DEFAULT_PARAMS = {"depth": 5, "deviation": 1.0, "wr_len": 14, "ob": -20.0, "os": -80.0, "sl_pct": 1.0, "tp_pct": 2.0}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date. The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _daily(raw_1m_df):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    if ohlc.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    bars = ohlc.groupby(broker_day(ohlc.index)).agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"}).dropna(how="all")
    start = (bars.index - pd.Timedelta(days=1) + pd.Timedelta(hours=17)).tz_localize("America/New_York")
    bars.index = start.tz_convert("UTC")  # each bar stamped with its session start
    return bars


def _multiday(raw_1m_df, days=2):
    """Blocks of `days` broker-day dates counted from 1970-01-01, stamped with the first session start (#426509)."""
    daily = _daily(raw_1m_df)
    day = broker_day(daily.index)
    key = np.asarray((day - pd.Timestamp("1970-01-01")).days // days)
    grouped = daily.assign(_key=key, _start=daily.index).groupby("_key", sort=True)
    bars = grouped.agg(open=("open", "first"), high=("high", "max"), low=("low", "min"),
                       close=("close", "last"), _start=("_start", "first"))
    return bars.set_index("_start").rename_axis(None)[["open", "high", "low", "close"]]


def precompute(raw_1m_df, symbol_key, **params):
    return _multiday(raw_1m_df, days=2)


def _pivots(x, lb, rb, high):
    m = len(x)
    out = np.zeros(m, dtype=bool)
    for t in range(lb + rb, m):
        j = t - rb
        v = x[j]
        if np.isnan(v):
            continue
        left, right = x[j - lb:j], x[j + 1:t + 1]
        if np.isnan(left).any() or np.isnan(right).any():
            continue
        out[t] = (v > left.max() and v > right.max()) if high else (v < left.min() and v < right.min())
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    hv, lv = h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    dp = int(p["depth"])
    ph, pl = _pivots(hv, dp, dp, True), _pivots(lv, dp, dp, False)
    dev = p["deviation"] / 100
    m = len(hv)
    zz = np.zeros(m)
    d, last_h, last_l = 0, np.nan, np.nan
    for i in range(m):
        if ph[i] and d != -1 and (np.isnan(last_h) or hv[i - dp] > last_h * (1 + dev)):
            last_h, d = hv[i - dp], -1
        if pl[i] and d != 1 and (np.isnan(last_l) or lv[i - dp] < last_l * (1 - dev)):
            last_l, d = lv[i - dp], 1
        zz[i] = d
    n = int(p["wr_len"])
    hh, ll = h.rolling(n).max(), lo.rolling(n).min()
    wr = (hh - c) / (hh - ll) * -100
    up = (wr > p["os"]) & (wr.shift(1) <= p["os"])
    dn = (wr < p["ob"]) & (wr.shift(1) >= p["ob"])
    long_e = (up & pd.Series(zz == 1, index=c.index)).astype(bool)
    short_e = (dn & pd.Series(zz == -1, index=c.index)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": p["sl_pct"] / 100, "tp_stop": p["tp_pct"] / 100}


def portfolio_kwargs(**params):
    return {}
