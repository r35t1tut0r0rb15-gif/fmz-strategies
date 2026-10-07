"""BEST Engulfing + MA: when the latest engulfing candle and the latest close/SMA 32 cross agree,
a new agreement that is more recent than the opposite one goes long (or short); a close beyond
the SMA closes the side; each entry carries a target and a stop fixed at the signal.
Port of FMZ strategy #365600 "BEST Engulfing + MA".

Source
    https://www.fmz.com/strategy/365600 (PineScript v4, FMZ last modified 2022-05-25 14:40:18).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 96-283), SMA 32 of close, TP 2000 USD, SL 200 USD
    Engulf_Buy = barssince(bullish engulfing) < barssince(bearish engulfing)   (Sell mirrors)
    bullish_MA = barssince(crossover(close, MA)) < barssince(crossunder(close, MA))
    conditionUP = Engulf_Buy and bullish_MA newly true;  conditionDN mirrors
    nUP = crossunder(barssince(conditionUP), barssince(conditionDN));  nDN = crossover(...)
    nUP -> entry long; exit(limit = close_at_nUP + 2000, stop = close_at_nUP - 200)
    strategy.close("Long") when close[1] < MA   (shorts mirror)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the 2000 / 200 USD distances are price units. They become tp_atr / sl_atr x
      ATR(14) at the signal bar: stops() returns tp_stop / sl_stop fractions of the signal close,
      shifted one bar inside stops(); vbt re-bases them on the fill price.
    * close[1] < MA is a close-based exit (rule 3): an exit signal, not a stop. On the signal
      bar itself the position is not yet open, so the close does not apply there (Pine ignores
      a close for an entry that is not open).
    * The 2017-2020 backtest window is replaced by testPeriod() => true in the source: dropped.
      pyramiding = 2 never applies (nUP and nDN alternate) -> original_sizing.txt.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "30min" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_365600_engulfing_ma_bracket"
FAMILY = "candle_pattern"  # proposed 2026-10-07, user to confirm
FREQ = "30min"  # backtest header period: 30m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True
ATR_LEN = 14  # criterion 2 conversion length (fixed)

GRID = {
    "length_ma": [20, 32, 50],
    "sl_atr": [1.0, 2.0],
    "tp_atr": [5.0, 10.0],
}
DEFAULT_PARAMS = {"length_ma": 32, "sl_atr": 1.0, "tp_atr": 10.0}


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


def _barssince(cond):
    out = np.full(len(cond), np.nan)
    last = -1
    for i, v in enumerate(cond):
        if v:
            last = i
        if last >= 0:
            out[i] = i - last
    return out


def _signals(bars_df, p):
    o, c = bars_df["open"], bars_df["close"]
    body = (c - o).abs()
    green, red = c > o, c < o
    hi_b, lo_b = np.maximum(c, o), np.minimum(c, o)
    hi_b1, lo_b1 = hi_b.shift(1), lo_b.shift(1)
    bigger = body > body.shift(1)
    bull = ((hi_b1 < hi_b) & bigger & green & red.shift(1, fill_value=False)).to_numpy()
    bear = (((hi_b1 < hi_b) & (lo_b1 > lo_b)) | ((hi_b1 >= hi_b) & (lo_b1 > lo_b))).to_numpy() \
        & (bigger & red & green.shift(1, fill_value=False)).to_numpy()
    ma = c.rolling(int(p["length_ma"])).mean()
    x_up = ((c > ma) & (c.shift(1) <= ma.shift(1))).to_numpy()
    x_dn = ((c < ma) & (c.shift(1) >= ma.shift(1))).to_numpy()
    e_cur = _barssince(bull) - _barssince(bear)
    m_cur = _barssince(x_up) - _barssince(x_dn)
    pos_up = (e_cur < 0).astype(int) + (m_cur < 0).astype(int)
    pos_dn = (e_cur > 0).astype(int) + (m_cur > 0).astype(int)
    lag = lambda a: np.concatenate([[np.nan], a[:-1].astype(float)])
    cond_up = (pos_up == 2) & (lag(pos_up) < 2)
    cond_dn = (pos_dn == 2) & (lag(pos_dn) < 2)
    s_up, s_dn = _barssince(cond_up), _barssince(cond_dn)
    n_up = (s_up < s_dn) & (lag(s_up) >= lag(s_dn))
    n_dn = (s_up > s_dn) & (lag(s_up) <= lag(s_dn))
    cv = c.to_numpy(dtype=float)
    long_close = np.concatenate([[np.nan], cv[:-1]]) < ma.to_numpy()
    short_close = np.concatenate([[np.nan], cv[:-1]]) > ma.to_numpy()
    return n_up, n_dn, long_close, short_close


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    n_up, n_dn, lc, sc = _signals(bars_df, p)
    idx = bars_df.index
    lx = lc & ~n_up & ~n_dn
    sx = sc & ~n_up & ~n_dn
    return (pd.Series(n_up, index=idx), pd.Series(lx, index=idx),
            pd.Series(n_dn & ~n_up, index=idx), pd.Series(sx, index=idx))


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    n_up, n_dn, _, _ = _signals(bars_df, p)
    atr_frac = _atr_pine(bars_df, ATR_LEN) / bars_df["close"]
    sig = pd.Series(n_up | n_dn, index=bars_df.index)
    sl = (p["sl_atr"] * atr_frac).where(sig)
    tp = (p["tp_atr"] * atr_frac).where(sig)
    return {"sl_stop": sl.shift(1), "tp_stop": tp.shift(1)}


def portfolio_kwargs(**params):
    return {}
