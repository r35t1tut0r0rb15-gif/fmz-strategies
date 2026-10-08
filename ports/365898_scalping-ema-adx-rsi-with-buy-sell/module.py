"""EMA / RSI / ADX scalper: above EMA 50 (low > EMA), with RSI(3) oversold within the last three
bars, ADX(5) > 30 and a close above the previous high, go long; the mirror goes short.
Port of FMZ strategy #365898 "EMA RSI ADX Scalping Alerts".

Source
    https://www.fmz.com/strategy/365898 (PineScript v5, FMZ last modified 2022-05-26 17:11:01).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 77-172), EMA 50, RSI 3 (80 / 20), ADX 5 / DI 5, limit 30
    long  = low > ema and min(rsi, rsi[1], rsi[2]) <= 20 and adx > 30 and close > high[1]
    short = high < ema and max(rsi, rsi[1], rsi[2]) >= 80 and adx > 30 and close < low[1]
    long -> entry long; else short -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * MA type default EMA; the MA rule is on by default. ADX as Pine's dirmov/adx (RMA, fixnan).
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "5min" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_365898_ema_rsi_adx_scalper"
FAMILY = "ma_trend_oscillator_pullback"  # proposed 2026-10-07, user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_len": [20, 50, 100],
    "rsi_len": [3, 5],
    "adx_limit": [25, 30],
}
DEFAULT_PARAMS = {"ema_len": 50, "rsi_len": 3, "rsi_ob": 80, "rsi_os": 20, "adx_len": 5, "di_len": 5,
                  "adx_limit": 30}


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
    h, l, c = bars_df["high"], bars_df["low"], bars_df["close"]
    ema = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    rsi = _rsi(c, int(p["rsi_len"]))
    os_ = (rsi <= p["rsi_os"]) | (rsi.shift(1) <= p["rsi_os"]) | (rsi.shift(2) <= p["rsi_os"])
    ob = (rsi >= p["rsi_ob"]) | (rsi.shift(1) >= p["rsi_ob"]) | (rsi.shift(2) >= p["rsi_ob"])
    _, _, adx = _adx_pine(bars_df, int(p["di_len"]), int(p["adx_len"]))
    strong = adx > p["adx_limit"]
    long_ = ((l > ema) & os_ & strong & (c > h.shift(1))).to_numpy()
    short = ((h < ema) & ob & strong & (c < l.shift(1))).to_numpy()
    return _always_in(long_, short, bars_df.index)


def portfolio_kwargs(**params):
    return {}
