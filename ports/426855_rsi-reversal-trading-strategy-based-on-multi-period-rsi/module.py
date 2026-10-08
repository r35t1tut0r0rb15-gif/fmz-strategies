"""Noro's triple RSI top / bottom: when the RSIs of 2, 7 and 14 bars are all deeply oversold go long,
all overbought go short; a long is closed on a green bar with a body over a third of the
10-bar average body, a short on such a red bar.
Port of FMZ strategy #426855 "RSI Reversal Trading Strategy Based on Multi Period RSI".

Source
    https://www.fmz.com/strategy/426855 (PineScript v2/v3 syntax, FMZ last modified 2023-09-14 20:42:55).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 136-197), indicators 3, accuracy 3 (acc = 7)
    Noro RSI (rma; 100 if down == 0, 0 if up == 0) of close over 2 / 7 / 14 bars
    up = rsi2 < 12 and rsi7 < 24 and rsi14 < 36;  dn = rsi2 > 88 and rsi7 > 76 and rsi14 > 64
    exit = ((long and close > open) or (short and close < open)) and body > sma(body, 10) / 3
    up -> [close_all if short] entry long;  dn -> [close_all if long] entry short;  exit -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * Orders fill at the next open in issue order; a close_all closes whatever is open when it
      fills, so a reversal bar that also meets the exit ends flat. pyramiding 0.
    * The leverage lot is sizing; the date window is dropped.
    * REVERSAL INTENDED (portfolio_kwargs {}). FREQ = "45min" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426855_noro_triple_rsi"
FAMILY = "rsi_oscillator"  # proposed 2026-10-07, user to confirm
FREQ = "45min"  # backtest header period: 45m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "indi": [2, 3],
    "accuracy": [3, 5, 7],
}
DEFAULT_PARAMS = {"indi": 3, "accuracy": 3}


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


def _rsi_pine(close, n):
    """rsi() as Pine defines it: 100 when the average loss is 0, 0 when the average gain is 0."""
    d = close.diff()
    up, down = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    rsi = 100.0 - 100.0 / (1.0 + up / down)
    return rsi.mask(up == 0, 0.0).mask(down == 0, 100.0).where(up.notna() & down.notna())


def _noro_orders(up, dn, exit_long, exit_short):
    """Noro's order block, filled at the next open in issue order: [close_all if short] entry
    long (if up); [close_all if long] entry short (if dn); close_all (if the exit holds for the
    position at the close). A close_all closes whatever is open when it fills; pyramiding 0
    refuses a same-side entry. exit_long / exit_short are arrays over bars."""
    m = len(up)
    target = np.zeros(m, dtype=int)
    pos = 0
    for i in range(m):
        before = pos
        orders = []
        if up[i]:
            if before < 0:
                orders.append("close")
            orders.append("long")
        if dn[i]:
            if before > 0:
                orders.append("close")
            orders.append("short")
        if (before > 0 and exit_long[i]) or (before < 0 and exit_short[i]):
            orders.append("close")
        for o in orders:
            if o == "close":
                pos = 0
            elif o == "long" and pos == 0:
                pos = 1
            elif o == "long" and pos < 0:
                pos = 1
            elif o == "short" and pos == 0:
                pos = -1
            elif o == "short" and pos > 0:
                pos = -1
        target[i] = pos
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
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, c = bars_df["open"], bars_df["close"]
    r2, r7, r14 = (_rsi_pine(c, n) for n in (2, 7, 14))
    acc = 10 - p["accuracy"]
    ups = (r2 < 5 + acc).astype(int) + (r7 < 10 + acc * 2).astype(int) + (r14 < 15 + acc * 3).astype(int)
    dns = (r2 > 95 - acc).astype(int) + (r7 > 90 - acc * 2).astype(int) + (r14 > 85 - acc * 3).astype(int)
    up, dn = (ups >= p["indi"]).to_numpy(), (dns >= p["indi"]).to_numpy()
    body = (c - o).abs()
    big = body > body.rolling(10).mean() / 3
    x_long = ((c > o) & big).to_numpy()
    x_short = ((c < o) & big).to_numpy()
    return _emit(_noro_orders(up, dn, x_long, x_short), bars_df.index)


def portfolio_kwargs(**params):
    return {}
