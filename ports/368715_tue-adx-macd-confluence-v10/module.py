"""TUE ADX / MACD confluence (Zer3192): +DI above -DI with MACD above its signal is the long state,
the mirror is the short state; entering the long state goes long, the short state short.
Port of FMZ strategy #368715 "TUE ADX/MACD Confluence V1.0".

Source
    https://www.fmz.com/strategy/368715 (PineScript v5, author Zer3192, FMZ last modified
    2022-06-12 14:01:56). Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 49-110), DMI 14 / 10, MACD 12 / 26 / 9
    longcheck = DI+ > DI- and macd > signal;  shortcheck = DI- > DI+ and signal > macd
    trade (re-declared 0 each bar) := longcheck ? 1 : shortcheck ? -1 : trade[1]
    trade turns 1 -> entry long; trade turns -1 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * trade is re-declared 0 on every bar, so only the "trade == 0" branches and the final else
      (trade[1]) can run: trade = longcheck ? 1 : shortcheck ? -1 : trade[1].
    * DI as Pine's ta.dmi (RMA, fixnan). strategy.entry reverses: REVERSAL INTENDED.
    * FREQ = "4h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_368715_dmi_macd_confluence"
FAMILY = "directional_movement"  # proposed 2026-10-07, user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "di_len": [10, 14, 20],
    "macd_fast": [8, 12],
}
DEFAULT_PARAMS = {"di_len": 14, "adx_smooth": 10, "macd_fast": 12, "macd_slow": 26, "macd_signal": 9}


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


def _fixnan(v):
    """Pine fixnan: replace na by the last non-na value (past values only)."""
    out = np.array(v, dtype=float)
    for i in range(1, len(out)):
        if np.isnan(out[i]):
            out[i] = out[i - 1]
    return out


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
    plus, minus, _ = _adx_pine(bars_df, int(p["di_len"]), int(p["adx_smooth"]))
    c = bars_df["close"]
    macd = c.ewm(span=int(p["macd_fast"]), adjust=False).mean() - c.ewm(span=int(p["macd_slow"]), adjust=False).mean()
    sig = macd.ewm(span=int(p["macd_signal"]), adjust=False).mean()
    lc = ((plus > minus) & (macd > sig)).to_numpy()
    sc = ((minus > plus) & (sig > macd)).to_numpy()
    m = len(c)
    trade = np.zeros(m)
    for i in range(m):
        trade[i] = 1.0 if lc[i] else (-1.0 if sc[i] else (trade[i - 1] if i else 0.0))
    prev = np.concatenate([[np.nan], trade[:-1]])
    return _always_in((trade == 1) & (prev != 1), (trade == -1) & (prev != -1), bars_df.index)


def portfolio_kwargs(**params):
    return {}
