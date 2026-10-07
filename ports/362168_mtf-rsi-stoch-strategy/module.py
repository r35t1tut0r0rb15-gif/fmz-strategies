"""Average of RSI(14) and of Stoch(14,3) over weekly, daily, 4-hour and 1-hour bars: long when
both averages are oversold, short when both are overbought; each side is closed when the
averages recover past the middle in profit.
Port of FMZ strategy #362168 "MTF-RSI-STOCH-Strategy".

Source
    https://www.fmz.com/strategy/362168 (PineScript v5, FMZ last modified 2022-05-10 12:06:12).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 58-145), chart 1d; timeframes W, D, 240, 60
    AVG = round(mean of RSI(14) on W, D, 4h, 1h, 2); AVG_STOCH likewise for sma(stoch(14),3)
    AVG <= 30 and AVG_STOCH <= 30 -> entry long
    close long when AVG_STOCH >= 70 and AVG >= 50 and close >= entry price
    AVG >= 70 and AVG_STOCH >= 70 -> entry short
    close short when AVG_STOCH <= 30 and AVG <= 50 and close <= entry price

Interpretation choices (Pine rules in SURVEY_README.md)
    * The chart is daily; the 4h and 1h values are the last intraday bars of the day. The port
      runs on 1-hour bars and decides only on the bar ending at the broker-day close (17:00 New
      York), filling at the next open (the daily chart's timing). 4-hour bars are built from the
      hourly bars on 4-hour blocks of the broker day; daily bars are broker days.
    * request.security with lookahead_off on historical bars gives the last COMPLETED higher bar;
      the port uses the weekly values of the weeks completed before the current one (it does not
      add the week ending on its last day; a one-day lag on that day only).
    * Entry price = the fill (next hourly open after the signal).
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_362168_mtf_rsi_stoch_average"
FAMILY = "rsi_oscillator"  # proposed 2026-10-07, user to confirm
FREQ = "1h"  # daily chart (backtest 1d) reading W/D/240/60 values: built from hourly bars
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_len": [9, 14, 21],
    "k_len": [9, 14, 21],
}
DEFAULT_PARAMS = {"rsi_len": 14, "k_len": 14, "smooth_k": 3, "rsi_os": 30, "rsi_ob": 70,
                  "stoch_os": 30, "stoch_ob": 70}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date. The desktop binds this name to registry_schema.broker_day."""
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


def _rma(x, n):
    """Wilder smoothing as TA-Lib: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def _rsi(close, n):
    d = close.diff()
    return 100.0 - 100.0 / (1.0 + _rma(d.clip(lower=0), n) / _rma((-d).clip(lower=0), n))


def _stoch(h, lo, c, k, smooth):
    hh, ll = h.rolling(k).max(), lo.rolling(k).min()
    return (100 * (c - ll) / (hh - ll)).replace([np.inf, -np.inf], np.nan).rolling(smooth).mean()


def _agg(bars, key):
    g = bars.groupby(key)
    return g.agg(high=("high", "max"), low=("low", "min"), close=("close", "last"))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    rn, kn, sk = int(p["rsi_len"]), int(p["k_len"]), int(p["smooth_k"])
    idx = bars_df.index
    ny = idx.tz_convert("America/New_York")
    day = broker_day(idx)
    block = ((ny.hour - 17) % 24) // 4                       # 4-hour block of the broker day
    k4 = np.asarray(day.values.astype("datetime64[h]").astype(np.int64) * 10 + np.asarray(block))
    week = np.asarray(day - pd.to_timedelta(day.weekday, unit="D"))

    def indicators(b):
        return _rsi(b["close"], rn), _stoch(b["high"], b["low"], b["close"], kn, sk)

    r1, s1 = indicators(bars_df)
    b4 = _agg(bars_df, k4)
    r4, s4 = (x.reindex(k4).to_numpy() for x in indicators(b4))
    bd = _agg(bars_df, day)
    rd, sd = (x.reindex(day).to_numpy() for x in indicators(bd))
    bw = _agg(bd, np.asarray(bd.index - pd.to_timedelta(bd.index.weekday, unit="D")))
    rw, sw = (x.shift(1).reindex(week).to_numpy() for x in indicators(bw))   # completed weeks
    avg = np.round((rw + rd + r4 + r1.to_numpy()) / 4, 2)
    avg_s = np.round((sw + sd + s4 + s1.to_numpy()) / 4, 2)
    end_ny = (idx + pd.Timedelta(hours=1)).tz_convert("America/New_York")
    at_close = np.asarray((end_ny.hour == 17) & (end_ny.minute == 0))
    o = bars_df["open"].to_numpy(dtype=float)
    c = bars_df["close"].to_numpy(dtype=float)

    m = len(c)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos, pending, entry = 0, 0, np.nan
    for i in range(m):
        if pending:
            pos, entry, pending = pending, o[i], 0
        if not at_close[i] or np.isnan(avg[i]) or np.isnan(avg_s[i]):
            continue
        if avg[i] <= p["rsi_os"] and avg_s[i] <= p["stoch_os"] and pos != 1:
            le[i], pending = True, 1
        elif avg[i] >= p["rsi_ob"] and avg_s[i] >= p["stoch_ob"] and pos != -1:
            se[i], pending = True, -1
        elif pos == 1 and avg_s[i] >= 70 and avg[i] >= 50 and c[i] >= entry:
            lx[i], pos = True, 0
        elif pos == -1 and avg_s[i] <= 30 and avg[i] <= 50 and c[i] <= entry:
            sx[i], pos = True, 0

    return (pd.Series(le, index=idx), pd.Series(lx, index=idx),
            pd.Series(se, index=idx), pd.Series(sx, index=idx))


def portfolio_kwargs(**params):
    return {}
