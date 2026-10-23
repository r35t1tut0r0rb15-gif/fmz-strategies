"""2-hour bars: a green bar closing above the EMA 10, EMA 20, session VWAP and EMA 200 with EMA 10 > EMA 20 > VWAP > EMA 200 goes long with a stop 1 ATR 14 under the 10-bar low and a target at twice that risk; the mirror goes short; reversing.
Port of FMZ strategy #482823 "Multi Timeframe VWAP and EMA Breakout Trading Strategy" (VWAP EMA Breakout).

FMZ source id: 482823

Source
    https://www.fmz.com/strategy/482823 (PineScript v5, FMZ last modified 2025-02-20 13:25:02).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 94-157), EMA 10 / 20 / 200; session VWAP; ATR 14; swing 10; targets 1 : 2 and 1 : 3 with one stop
    longCondition = close above EMA 10 / 20 / VWAP / EMA 200 and close > open and ema10 > ema20 > vwap > ema200 -> entry Long, exit("TP 1:2", limit = close + 2 risk, stop = lowest(low, 10) - atr), exit("TP 1:3", limit = close + 3 risk, same stop)
    shortCondition mirrored -> entry Short, exits "TP 1:2" / "TP 1:3" from_entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Both exits close the whole position, so the 1 : 2 target (the nearer) and the shared stop decide.
      Each side's exits are sent on its own signal bars (which never coincide), as levels from that bar:
      ported as fractions of the fill, exact (1e-6 floor). The long set-up is a state that repeats while
      the trend lasts, and each repeat re-sends the levels from the new bar (not followed:
      trailing_stop_pending). ta.vwap(close) restarts each session: the house session is the broker day
      (17:00 America/New_York). REVERSAL INTENDED. No sizing code. Stop module: portfolio_kwargs {}
      (driver D4). Stops on 2-hour bars: coarse_bar_stop. FREQ = "2h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; swing-ATR bracket at the signal bar as fractions of the fill.
    2 generic: PASS, aligned EMA / VWAP trend candles.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) as the session-VWAP weights; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone) for the VWAP reset; no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_482823_ema_vwap_stack_candle_swing_atr_rr2_2h_reversal"
FAMILY = "vwap"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "rr": [2.0, 3.0],
    "swing": [10, 20],
}
DEFAULT_PARAMS = {"rr": 2.0, "swing": 10}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def _rma(x, n):
    """Wilder smoothing as Pine's rma: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    return _rma(pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1), n)


def simulate(bars_df, **params):
    o, c, v = bars_df["open"], bars_df["close"], bars_df["volume"]
    day = broker_day(bars_df.index)
    vw = (c * v).groupby(day).cumsum() / v.groupby(day).cumsum()
    e10, e20, e200 = (c.ewm(span=n, adjust=False).mean() for n in (10, 20, 200))
    buy = (c > vw) & (c > e200) & (c > e10) & (c > e20) & (c > o) & (e10 > e20) & (e20 > vw) & (vw > e200)
    sell = (c < vw) & (c < e200) & (c < e10) & (c < e20) & (c < o) & (e10 < e20) & (e20 < vw) & (vw < e200)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return buy.astype(bool), false, sell.astype(bool), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx, se, sx = simulate(bars_df, **params)
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    atr = _atr(bars_df, 14)
    n, rr = int(p["swing"]), float(p["rr"])
    sl_l = lo.rolling(n).min() - atr
    sl_s = h.rolling(n).max() + atr
    tp_l = c + (c - sl_l) * rr
    tp_s = c - (sl_s - c) * rr
    lf, sf = le.shift(1, fill_value=False), se.shift(1, fill_value=False)
    sl_f = (pd.Series(np.nan, index=o.index).mask(lf, 1 - sl_l.shift(1) / o)
            .mask(sf, sl_s.shift(1) / o - 1))
    tp_f = (pd.Series(np.nan, index=o.index).mask(lf, tp_l.shift(1) / o - 1)
            .mask(sf, 1 - tp_s.shift(1) / o))
    return {"sl_stop": sl_f.clip(lower=1e-6), "tp_stop": tp_f.clip(lower=1e-6)}


def portfolio_kwargs(**params):
    return {}
