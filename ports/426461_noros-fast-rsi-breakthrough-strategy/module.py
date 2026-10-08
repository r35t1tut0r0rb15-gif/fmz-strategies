"""Noro's fast RSI v1.6: a red bar with the fast RSI(7) under 30 (or two red bars in a row, or a
red bar making a lower min(open, close) after another red bar) goes long; the mirrors go short.
A long is closed on a green bar with RSI over 30 and a body over half the 10-bar average body
(a short on such a red bar under 70).
Port of FMZ strategy #426461 "Noro's Fast RSI Breakthrough Strategy".

Source
    https://www.fmz.com/strategy/426461 (PineScript v2/v3 syntax, FMZ last modified 2023-09-12 11:40:44).
    Verbatim copy: original_source.md. Read 2026-10-08 (re-read; rejected in batch A19 as a
    pyramided ladder, which SURVEY_README classes as sizing).

Original signal (original_source.md lines 183-249), RSI 7, limit 30, RSI / min-max bars 1,
SMA filter off, all three rules on, pyramiding 10
    fastrsi = Noro RSI (rma 7; 100 if down == 0, 0 if up == 0); bar = sign(close - open)
    up1 = bar == -1 and (flat or close < avg price) and fastrsi < 30 and body > sma(body, 10) / 5
    up2 = min(close, open) < its previous value and bar == -1 and bar[1] == -1 and fastrsi < 70
    up3 = sma(bar, 2) == -1                          (dn1 / dn2 / dn3 mirror)
    exit = ((long and fastrsi > 30 and bar == 1) or (short and fastrsi < 70 and bar == -1))
           and body > sma(body, 10) / 2
    up -> [close_all if short] entry long;  dn -> [close_all if long] entry short;  exit -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * pyramiding 10: same-side entries while in a position are adds, i.e. sizing; the port emits
      the net position. The average price is the position's first fill.
    * Orders fill at the next open in issue order; a close_all closes whatever is open when it
      fills. REVERSAL INTENDED (portfolio_kwargs {}).
    * The date window is dropped. Daily bars are broker days (session ending 17:00 New York),
      stamped with the session start.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426461_noro_fast_rsi_v16"
FAMILY = "rsi_oscillator"  # proposed 2026-10-07, user to confirm
FREQ = "1D"  # broker days (backtest period 1d)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [5, 7],
    "limit": [20, 30],
}
DEFAULT_PARAMS = {"fast": 7, "limit": 30}


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


def _rsi_pine(close, n):
    """rsi() as Pine defines it: 100 when the average loss is 0, 0 when the average gain is 0."""
    d = close.diff()
    up, down = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    rsi = 100.0 - 100.0 / (1.0 + up / down)
    return rsi.mask(up == 0, 0.0).mask(down == 0, 100.0).where(up.notna() & down.notna())


def _noro_net(o, c, up_any, up_avg, dn_any, dn_avg, exit_long, exit_short):
    """Net position of Noro's order block, filled at the next open in issue order:
    up -> [close_all if short] entry long; dn -> [close_all if long] entry short; exit ->
    close_all. up = up_any or (up_avg and (flat or close < average price)); dn mirrors with
    close > average price. The average price is the first fill of the position (adds under
    pyramiding are sizing). A close_all closes whatever is open when it fills."""
    m = len(c)
    target = np.zeros(m, dtype=int)
    prev, entry = 0, np.nan
    for i in range(m):
        if i > 0 and target[i - 1] != prev:      # the previous bar's orders filled at this open
            entry = o[i] if target[i - 1] != 0 else np.nan
        before = target[i - 1] if i > 0 else 0
        prev = before
        up = up_any[i] or (up_avg[i] and (before == 0 or c[i] < entry))
        dn = dn_any[i] or (dn_avg[i] and (before == 0 or c[i] > entry))
        p = before
        if up:
            if before < 0:
                p = 0
            if p <= 0:
                p = 1
        if dn:
            if before > 0:
                p = 0
            if p >= 0:
                p = -1
        if (before > 0 and exit_long[i]) or (before < 0 and exit_short[i]):
            p = 0
        target[i] = p
    return target


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


def precompute(raw_1m_df, symbol_key, **params):
    return _daily(raw_1m_df)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, c = bars_df["open"], bars_df["close"]
    rsi = _rsi_pine(c, int(p["fast"]))
    up_l, dn_l = 100 - p["limit"], p["limit"]
    bar = np.sign(c - o)
    body = (c - o).abs()
    abody = body.rolling(10).mean()
    mn, mx = np.minimum(c, o), np.maximum(c, o)
    two_red = (bar == -1) & (bar.shift(1) == -1)
    two_green = (bar == 1) & (bar.shift(1) == 1)
    up1 = ((bar == -1) & (rsi < dn_l) & (body > abody / 5)).to_numpy()
    dn1 = ((bar == 1) & (rsi > up_l) & (body > abody / 5)).to_numpy()
    up23 = (((mn < mn.shift(1)) & two_red & (rsi < 70)) | (bar.rolling(2).mean() == -1)).to_numpy()
    dn23 = (((mx > mx.shift(1)) & two_green & (rsi > 30)) | (bar.rolling(2).mean() == 1)).to_numpy()
    x_long = ((rsi > dn_l) & (bar == 1) & (body > abody / 2)).to_numpy()
    x_short = ((rsi < up_l) & (bar == -1) & (body > abody / 2)).to_numpy()
    target = _noro_net(o.to_numpy(dtype=float), c.to_numpy(dtype=float), up23, up1, dn23, dn1, x_long, x_short)
    return _emit(target, bars_df.index)


def portfolio_kwargs(**params):
    return {}
