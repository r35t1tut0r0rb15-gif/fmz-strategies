"""3-minute SuperTrend (factor 1, ATR 7) direction changes from one daily bar to the next, confirmed by the previous day's 30-minute MACD (2, 8, 4) histogram, daily bars: a change to an uptrend closes a short
and, with the histogram above zero, goes long; a change to a downtrend closes a long and, with it below zero, goes short (the intraday clock branches never act on daily bars).
Port of FMZ strategy #444352 "Dynamic Intraday Long Short Balancing Strategy Combining Moving Average and Supertrend" (EQ - INTRA - Samsuga supertrend prod).

FMZ source id: 444352

Source
    https://www.fmz.com/strategy/444352 (PineScript v5, FMZ last modified 2024-03-11 11:33:47).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 133-208), SuperTrend factor 1, ATR 7 from the 3-minute time frame; MACD 2 / 8 / 4 from the 30-minute time frame (both lookahead on); day exit 15:15, open entry 09:30; timezone Asia/Kolkata (unused); 100 % of equity
    [st, direction] = security("3", supertrend(1, 7), lookahead_on);  hist = security("30", macd(close, 2, 8, 4), lookahead_on);  longcondition = direction[1] > direction;  shortCondition = direction[1] < direction
    hour == 15 and minute == 15 -> close all;  else hour == 9 and minute == 30 -> (long or hist[1] > 0) entry Long, else (short or hist[1] < 0) entry Short
    else: long -> close Short, hist[1] > 0 -> entry Long;  else short -> close Long, hist[1] < 0 -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The backtest header runs this on daily bars. A daily bar's time is its session start, at minute
      0, so neither the 15:15 day exit nor the 09:30 entry branch can ever be true; only the last
      branch acts, as written. The 3-minute and 30-minute values requested from a daily chart are the
      day's LAST 3-minute and 30-minute bars (a lower time frame returns its last bar inside the chart
      bar; lookahead does not change it, as #436765): the SuperTrend direction compared with the
      previous day's, and the previous day's histogram ([1]). The 3- and 30-minute bars are left-labelled
      from the minutes, gaps kept, and grouped by broker day. A close on a side not held never acts; a
      close and the opposite entry on one bar is one reversal. The timezone input is never used.
      REVERSAL INTENDED. The 100 % of equity size is sizing. FREQ = "1D" from the backtest header
      (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the 3- and 30-minute values end with the daily bar.
    2 generic: PASS, day-to-day changes of the 3-minute SuperTrend direction with a MACD filter.
    3 crypto-exchange-only: no (exchange pair in the header only; the Asia/Kolkata timezone input is never used).
    4 signals only: the 100 % of equity size stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); the clock branches never act on daily bars.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_444352_daily_3m_supertrend_change_30m_macd_reversal"
FAMILY = "multi_timeframe_ma"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "factor": [1.0, 3.0],
    "atr_period": [7, 14],
}
DEFAULT_PARAMS = {"factor": 1.0, "atr_period": 7, "fast": 2, "slow": 8, "signal": 4}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _resample(df, freq):
    bars = df.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    return bars.dropna(how="all")  # an empty period is not a bar; never forward-filled


def _supertrend_dir(h, lo, c, factor, n):
    """Direction of Pine's supertrend(factor, atrPeriod): -1 uptrend, 1 downtrend, nan before the ATR."""
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    tr.iloc[0] = np.nan
    atr = tr.ewm(alpha=1 / n, adjust=False).mean().to_numpy()
    hl2 = ((h + lo) / 2).to_numpy(dtype=float)
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    lb, ub, st = np.full(m, np.nan), np.full(m, np.nan), np.full(m, np.nan)
    d = np.full(m, np.nan)
    for i in range(m):
        lo_b, up_b = hl2[i] - factor * atr[i], hl2[i] + factor * atr[i]
        pl = lb[i - 1] if i > 0 and not np.isnan(lb[i - 1]) else 0.0
        pu = ub[i - 1] if i > 0 and not np.isnan(ub[i - 1]) else 0.0
        cp = cv[i - 1] if i > 0 else np.nan
        lb[i] = lo_b if (lo_b > pl or cp < pl) else pl
        ub[i] = up_b if (up_b < pu or cp > pu) else pu
        if np.isnan(atr[i]):
            lb[i], ub[i] = np.nan, np.nan
            continue
        if i == 0 or np.isnan(atr[i - 1]):
            up_dir = False
        elif st[i - 1] == ub[i - 1]:
            up_dir = cv[i] > ub[i]
        else:
            up_dir = not (cv[i] < lb[i])
        st[i] = lb[i] if up_dir else ub[i]
        d[i] = -1.0 if up_dir else 1.0
    return pd.Series(d, index=c.index)


def precompute(raw_1m_df, symbol_key, **params):
    p = {**DEFAULT_PARAMS, **params}
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    m3 = _resample(df, "3min")
    d3 = _supertrend_dir(m3["high"], m3["low"], m3["close"], float(p["factor"]), int(p["atr_period"]))
    bars["dir3"] = d3.groupby(broker_day(m3.index)).last()           # the day's last 3-minute bar
    m30 = _resample(df, "30min")
    c = m30["close"]
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    hist = macd - macd.ewm(span=int(p["signal"]), adjust=False).mean()
    bars["hist30"] = hist.groupby(broker_day(m30.index)).last()       # the day's last 30-minute bar
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def simulate(bars_df, **params):
    d = bars_df["dir3"]
    d1 = d.shift(1)
    lc = (d1 > d).to_numpy()
    sc = (d1 < d).to_numpy()
    h1 = bars_df["hist30"].shift(1).to_numpy()
    m = len(lc)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    with np.errstate(invalid="ignore"):
        for i in range(m):
            if lc[i]:
                if h1[i] > 0:
                    if pos != 1:
                        le[i], pos = True, 1          # a held short reverses
                elif pos == -1:
                    sx[i], pos = True, 0
            elif sc[i]:
                if h1[i] < 0:
                    if pos != -1:
                        se[i], pos = True, -1
                elif pos == 1:
                    lx[i], pos = True, 0
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
