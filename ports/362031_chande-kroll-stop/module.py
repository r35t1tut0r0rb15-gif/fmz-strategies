"""Chande Kroll stop crosses with an ADX filter, traded as written: close crossing DOWN through
the long stop goes LONG, close crossing UP through the short stop goes SHORT.
Port of FMZ strategy #362031 "Chande-Kroll-Stop".

Source
    https://www.fmz.com/strategy/362031 (PineScript v5, FMZ last modified 2022-05-09 17:44:31).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 42-75), p 10, x 1, q 9, ADX 14/14 > 20
    first_high_stop = highest(high,p) - x*atr(p); first_low_stop = lowest(low,p) + x*atr(p)
    stop_short = highest(first_high_stop, q); stop_long = lowest(first_low_stop, q)
    crossunder(close, stop_long) and adx > 20 -> entry long
    crossover(close, stop_short) and adx > 20 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The Chande Kroll lines are used as entry triggers in the opposite sense to their usual
      reading (a break below the long stop buys). Ported as written (flagged).
    * Two separate `if`s: if both fire on one bar, the later (short) decides. strategy.entry
      reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * ADX as Pine's dirmov/adx (RMA, fixnan). `x` is `true` (= 1) in FMZ's argument table.
    * No backtest header: FREQ = "bar_size_pending" (rule 1).

Marks: bar_size_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_362031_chande_kroll_cross_faded"
FAMILY = "volatility_stop_cross"  # proposed 2026-10-07, user to confirm
FREQ = "bar_size_pending"  # source declares no bar size; set by the project before running
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "p": [10, 20],
    "q": [9, 20],
    "x": [1.0, 2.0],
}
DEFAULT_PARAMS = {"p": 10, "q": 9, "x": 1.0, "adx_len": 14, "di_len": 14, "adx_min": 20}


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


def _atr_pine(bars, n):
    """ta.atr: Wilder RMA of the true range; the first bar's range is high - low (ta.tr(true))."""
    prev_close = bars["close"].shift(1)
    tr = pd.concat([bars["high"] - bars["low"],
                    (bars["high"] - prev_close).abs(),
                    (bars["low"] - prev_close).abs()], axis=1).max(axis=1)
    return _rma(tr, n)


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


def _always_in(long_sig, short_sig, index, short_first=False):
    """Stop-and-reverse from two condition arrays (first matching line in source order wins)."""
    m = len(long_sig)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        first, second = ((short_sig, -1), (long_sig, 1)) if short_first else ((long_sig, 1), (short_sig, -1))
        for sig, side in (first, second):
            if sig[i]:
                if pos != side:
                    (le if side == 1 else se)[i] = True
                    pos = side
                break
    false = pd.Series(False, index=index)
    return pd.Series(le, index=index), false.copy(), pd.Series(se, index=index), false.copy()


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    n, q = int(p["p"]), int(p["q"])
    atr = _atr_pine(bars_df, n)
    fh = bars_df["high"].rolling(n).max() - p["x"] * atr
    fl = bars_df["low"].rolling(n).min() + p["x"] * atr
    stop_short, stop_long = fh.rolling(q).max(), fl.rolling(q).min()
    c = bars_df["close"]
    adx = _adx_pine(bars_df, int(p["di_len"]), int(p["adx_len"]))[2]
    strong = (adx > p["adx_min"]).to_numpy()
    go_long = ((c < stop_long) & (c.shift(1) >= stop_long.shift(1))).to_numpy() & strong
    go_short = ((c > stop_short) & (c.shift(1) <= stop_short.shift(1))).to_numpy() & strong
    return _always_in(go_long, go_short, bars_df.index, short_first=True)


def portfolio_kwargs(**params):
    return {}
