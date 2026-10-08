"""Hull + Ichimoku + MACD with a daily-return filter: from flat, go long when the double Hull (14)
is above its previous value and under the close, the last completed day closed up more than
0.1 %, the cloud is green, the bar is green and MACD is above its signal (shorts mirrored); close
when the Hull turns back with the close across it and the day filter reversed.
Port of FMZ strategy #426842 "Multi Indicator Short Term Algorithmic Trading Strategy".

Source
    https://www.fmz.com/strategy/426842 (PineScript v2/v3 syntax, FMZ last modified 2023-09-14 19:46:55).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 144-189), Hull 14, dt 0.001, Ichimoku 9 / 26 / 52,
MACD 12 / 26 / 9
    n1 = wma(2 wma(close, 7) - wma(close, 14), 4); n2 = the same on close[1]
    confidence = (D close - D close[1]) / D close[1]        (security 'D', lookahead off)
    closelong  = n1 < n2 and close < n2 and confidence < dt (or openprofit < -500 / > 25000 $)
    closeshort = n1 > n2 and close > n2 and confidence > dt (or the same $ thresholds)
    long  = n1 > n2 and no open trade and confidence > dt and close > n2 and spanA > spanB
            and open < close and macd > signal          (short mirrored)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The daily values run on broker days built from the 4h bars. Historical lookahead_off
      values are the last completed day's (the new day's value appears on the bar whose end
      reaches the day's 17:00 New York close).
    * The openprofit thresholds in account currency are balance checks: sizing
      (original_sizing.txt), not ported.
    * Closes are issued before entries and entries need no open trade at the close, so a bar
      that closes a trade does not open one. Opposite entries cannot occur.
    * FREQ = "4h" from the backtest header (the title's 15m is not the backtest period).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426842_hull_ichimoku_macd_dayfilter"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-07, user to confirm
FREQ = "4h"  # backtest header period: 4h
BAR_HOURS = 4
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "keh": [14, 21],
    "dt": [0.001, 0.005],
}
DEFAULT_PARAMS = {"keh": 14, "dt": 0.001, "conv": 9, "base": 26, "span_b": 52, "fast": 12, "slow": 26, "signal": 9}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _wma(x, n):
    """ta.wma: linearly weighted MA, weight n on the current bar."""
    n = int(n)
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda a: np.dot(a, w) / w.sum(), raw=True)


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date. The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _emit(target, index):
    """Signals from the position each bar's orders leave (1 / 0 / -1): a change to +-1 is an
    entry (reversing an opposite position), a change to 0 an exit of the side held."""
    m = len(target)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    prev = 0
    for i in range(m):
        n = target[i]
        if n != prev:
            if n == 1:
                le[i] = True
            elif n == -1:
                se[i] = True
            elif prev == 1:
                lx[i] = True
            else:
                sx[i] = True
        prev = n
    return tuple(pd.Series(x, index=index) for x in (le, lx, se, sx))


def _day_return(bars_df):
    """Last completed broker day's close-to-close return, as lookahead_off shows it."""
    day = broker_day(bars_df.index)
    dclose = bars_df["close"].groupby(day).last()
    dret = (dclose - dclose.shift(1)) / dclose.shift(1)
    end_ny = (bars_df.index + pd.Timedelta(hours=BAR_HOURS)).tz_convert("America/New_York")
    day_end_ny = (pd.DatetimeIndex(day) + pd.Timedelta(hours=17)).tz_localize("America/New_York")
    at_close = np.asarray(end_ny >= day_end_ny)
    today = dret.reindex(day).to_numpy()
    before = dret.shift(1).reindex(day).to_numpy()
    return np.where(at_close, today, before)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, l, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    k = int(p["keh"])
    hull = lambda x: _wma(2 * _wma(x, int(round(k / 2))) - _wma(x, k), int(round(np.sqrt(k))))
    n1, n2 = hull(c), hull(c.shift(1))
    conf = pd.Series(_day_return(bars_df), index=bars_df.index)
    don = lambda n: (l.rolling(int(n)).min() + h.rolling(int(n)).max()) / 2
    a = (don(p["conv"]) + don(p["base"])) / 2
    b = don(p["span_b"])
    ema = lambda x, n: x.ewm(span=int(n), adjust=False).mean()
    macd = ema(c, p["fast"]) - ema(c, p["slow"])
    sig = ema(macd, p["signal"])
    dt = p["dt"]
    x_long = ((n1 < n2) & (c < n2) & (conf < dt)).to_numpy()
    x_short = ((n1 > n2) & (c > n2) & (conf > dt)).to_numpy()
    long_c = ((n1 > n2) & (conf > dt) & (c > n2) & (a > b) & (o < c) & (macd > sig)).to_numpy()
    short_c = ((n1 < n2) & (conf < dt) & (c < n2) & (a < b) & (o > c) & (macd < sig)).to_numpy()
    target = np.zeros(len(c), dtype=int)
    pos = 0
    for i in range(len(c)):
        if pos == 1 and x_long[i]:
            pos = 0
        elif pos == -1 and x_short[i]:
            pos = 0
        elif pos == 0 and long_c[i]:
            pos = 1
        elif pos == 0 and short_c[i]:
            pos = -1
        target[i] = pos
    return _emit(target, bars_df.index)


def portfolio_kwargs(**params):
    return {}
