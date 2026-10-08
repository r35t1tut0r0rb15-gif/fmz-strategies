"""RAVI FX Fisher (Loxx): the volatility-adjusted gap between WMA 4 and WMA 49, squashed by a
Fisher (tanh) transform; non-negative is long, negative is short (always in).
Port of FMZ strategy #369392 "RAVI FX Fisher [Loxx]".

Source
    https://www.fmz.com/strategy/369392 (PineScript v5, FMZ last modified 2022-06-16 15:15:28).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 45-66), fast 4, slow 49, trigger 0.07 (unused)
    maval = 100 * (wma(close, 4) - wma(close, 49)) * atr(4) / wma(close, 49) / atr(49)
    fish = tanh(maval);  fish >= 0 -> entry long, else entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * (exp(2x) - 1) / (exp(2x) + 1) is tanh(x); its sign is the sign of maval. The trigger input
      is unused by the orders.
    * Daily bars are broker days (session ending 17:00 New York), stamped with the session start.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_369392_ravi_fisher_sign"
FAMILY = "ma_trend"  # proposed 2026-10-07, user to confirm
FREQ = "1D"  # broker days (backtest period 1d)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [4, 7],
    "slow": [49, 65],
}
DEFAULT_PARAMS = {"fast": 4, "slow": 49}


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


def _wma(x, n):
    """ta.wma: linearly weighted MA, weight n on the current bar."""
    n = int(n)
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda a: np.dot(a, w) / w.sum(), raw=True)


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
    return _daily(raw_1m_df)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    f, s = int(p["fast"]), int(p["slow"])
    ws = _wma(c, s)
    maval = 100 * (_wma(c, f) - ws) * _atr_pine(bars_df, f) / ws / _atr_pine(bars_df, s)
    fish = np.tanh(maval)
    up = (fish >= 0).to_numpy()  # na (warm-up) is not >= 0, so Pine's else branch goes short
    return _always_in(up, ~up, bars_df.index)


def portfolio_kwargs(**params):
    return {}
