"""Femi MACD / RSI, long only: the MACD histogram crossing above 0, or RSI(14) crossing under 30,
goes long; RSI crossing above 70, or ADX, the histogram and the close crossing under 25, 0 and
the upper Bollinger band on the same bar, closes it.
Port of FMZ strategy #426612 "Trend Following Strategy Based on Multiple Indicator Integration".

Source
    https://www.fmz.com/strategy/426612 (PineScript v4, FMZ last modified 2023-09-13 17:16:51).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 85-188), RSI 14 30 / 70, ADX 14 / 14 > 25, MACD 12 / 26 / 9,
BB 20 x 2
    when rsi is not na:
      crossover(delta, 0)    -> entry "FEMIMACDLE"
      crossunder(rsi, 30)    -> entry "FEMIRSILE"
      crossover(rsi, 70)     -> close all long ids
      crossunder(adx, 25) and crossunder(delta, 0) and crossunder(close, upper) -> close all

Interpretation choices (Pine rules in SURVEY_README.md)
    * strategy() sets no pyramiding, so only one long is held; the second entry id is refused
      while long. strategy.cancel only cancels unfilled orders (none at bar close).
    * Same bar: from flat an entry stands (the closes, tested at the close, find no position);
      while long an entry is refused and a close goes flat.
    * Long only (the short entries are commented out). stdev is Pine's population deviation.
    * FREQ = "1min" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426612_femi_macd_rsi_long"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-07, user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_len": [14, 21],
    "over_sold": [30, 25],
    "over_bought": [70, 75],
}
DEFAULT_PARAMS = {"rsi_len": 14, "over_sold": 30, "over_bought": 70, "adx_len": 14, "di_len": 14,
                  "adx_threshold": 25, "fast": 12, "slow": 26, "signal": 9, "bb_len": 20, "bb_mult": 2.0}


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


def _fixnan(v):
    """Pine fixnan: replace na by the last non-na value (past values only)."""
    out = np.array(v, dtype=float)
    for i in range(1, len(out)):
        if np.isnan(out[i]):
            out[i] = out[i - 1]
    return out


def _adx_pine(bars, di_len, adx_len):
    """Pine's built-in-style dirmov/adx: RMA smoothing, fixnan on DI+/DI-."""
    h, lo, c = bars["high"], bars["low"], bars["close"]
    up, down = h.diff(), -lo.diff()
    plus_dm = np.where(up.isna(), np.nan, np.where((up > down) & (up > 0), up, 0.0))
    minus_dm = np.where(down.isna(), np.nan, np.where((down > up) & (down > 0), down, 0.0))
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    trs = _rma(tr, di_len)
    plus = _fixnan((100 * _rma(pd.Series(plus_dm, index=h.index), di_len) / trs).to_numpy())
    minus = _fixnan((100 * _rma(pd.Series(minus_dm, index=h.index), di_len) / trs).to_numpy())
    s = plus + minus
    dx = pd.Series(np.abs(plus - minus) / np.where(s == 0, 1, s), index=h.index)
    return pd.Series(plus, index=h.index), pd.Series(minus, index=h.index), 100 * _rma(dx, adx_len)


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


def _xover(a, b):
    return (a > b) & (a.shift(1) <= (b.shift(1) if isinstance(b, pd.Series) else b))


def _xunder(a, b):
    return (a < b) & (a.shift(1) >= (b.shift(1) if isinstance(b, pd.Series) else b))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    rsi = _rsi_pine(c, int(p["rsi_len"]))
    ema = lambda x, n: x.ewm(span=int(n), adjust=False).mean()
    macd = ema(c, p["fast"]) - ema(c, p["slow"])
    delta = macd - ema(macd, p["signal"])
    _, _, adx = _adx_pine(bars_df, int(p["di_len"]), int(p["adx_len"]))
    n = int(p["bb_len"])
    upper = c.rolling(n).mean() + p["bb_mult"] * c.rolling(n).std(ddof=0)
    ok = rsi.notna()
    entry = (ok & (_xover(delta, 0.0) | _xunder(rsi, p["over_sold"]))).to_numpy()
    exit_ = (ok & (_xover(rsi, p["over_bought"])
                   | (_xunder(adx, p["adx_threshold"]) & _xunder(delta, 0.0) & _xunder(c, upper)))).to_numpy()
    target = np.zeros(len(c), dtype=int)
    pos = 0
    for i in range(len(c)):
        if pos == 0 and entry[i]:
            pos = 1
        elif pos == 1 and exit_[i]:
            pos = 0
        target[i] = pos
    return _emit(target, bars_df.index)


def portfolio_kwargs(**params):
    return {}
