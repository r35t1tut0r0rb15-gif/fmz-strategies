"""SSL channel + stochastic RSI (luqi0212): the 200-bar SSL channel flipping up, or the 20-bar one
flipping up with stoch-RSI %K and %D below 20, goes long; the mirrors go short. A fixed take-profit
and stop bracket every position.
Port of FMZ strategy #391341 "SSL Channel" + "Stoch RSI".

Source
    https://www.fmz.com/strategy/391341 (PineScript v5, author luqi0212, FMZ last modified
    2022-11-24 11:56:41). Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 74-178), SSL 200 / 20 (SMA of high / low), stoch RSI
14 / 14 / 3 / 3, profit 10000 ticks, loss 10000 ticks
    long  = Hlv1 turns 1 or (Hlv2 turns 1 and k < 20 and d < 20)   (Pine: `and` binds tighter)
    short = Hlv1 turns -1 or (Hlv2 turns -1 and k > 80 and d > 80)
    strategy.exit(profit = 10000, loss = 10000) on every bar

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the 10000-tick target and stop are instrument-specific (ETH: 100 USD). They
      become bracket_atr x ATR(14) at the signal bar, as tp_stop / sl_stop fractions shifted one
      bar inside stops(); vbt re-bases them on the fill price.
    * Two indicator() scripts were merged by the author; the stoch-RSI one only feeds the filter.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}). Quantity 20 -> sizing.
    * FREQ = "5min" from the backtest header (ETH pair in the header only).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_391341_ssl_stochrsi_bracket"
FAMILY = "ma_envelope_breakout"  # proposed 2026-10-07, user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True
ATR_LEN = 14  # criterion 2 conversion length (fixed)

GRID = {
    "ssl_slow": [100, 200],
    "ssl_fast": [10, 20],
    "bracket_atr": [5.0, 10.0, 20.0],
}
DEFAULT_PARAMS = {"ssl_slow": 200, "ssl_fast": 20, "rsi_len": 14, "stoch_len": 14, "k": 3, "d": 3,
                  "bracket_atr": 10.0}


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


def _atr_pine(bars, n):
    """ta.atr: Wilder RMA of the true range; the first bar's range is high - low (ta.tr(true))."""
    prev_close = bars["close"].shift(1)
    tr = pd.concat([bars["high"] - bars["low"],
                    (bars["high"] - prev_close).abs(),
                    (bars["low"] - prev_close).abs()], axis=1).max(axis=1)
    return _rma(tr, n)


def _hlv(bars_df, n):
    c = bars_df["close"]
    up = (c > bars_df["high"].rolling(n).mean()).to_numpy()
    dn = (c < bars_df["low"].rolling(n).mean()).to_numpy()
    out = np.full(len(c), np.nan)
    for i in range(len(c)):
        out[i] = 1.0 if up[i] else (-1.0 if dn[i] else (out[i - 1] if i else np.nan))
    return out


def _signals(bars_df, p):
    c = bars_df["close"]
    rsi = _rsi(c, int(p["rsi_len"]))
    s = int(p["stoch_len"])
    st = 100 * (rsi - rsi.rolling(s).min()) / (rsi.rolling(s).max() - rsi.rolling(s).min())
    k = st.rolling(int(p["k"])).mean()
    d = k.rolling(int(p["d"])).mean()
    h1, h2 = _hlv(bars_df, int(p["ssl_slow"])), _hlv(bars_df, int(p["ssl_fast"]))
    lag = lambda a: np.concatenate([[np.nan], a[:-1]])
    up1, dn1 = (h1 == 1) & (lag(h1) == -1), (h1 == -1) & (lag(h1) == 1)
    up2, dn2 = (h2 == 1) & (lag(h2) == -1), (h2 == -1) & (lag(h2) == 1)
    kv, dv = k.to_numpy(), d.to_numpy()
    long_ = up1 | (up2 & (kv < 20) & (dv < 20))
    short = dn1 | (dn2 & (kv > 80) & (dv > 80))
    return long_ & ~short, short & ~long_


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se = _signals(bars_df, p)
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), false.copy(), pd.Series(se, index=idx), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se = _signals(bars_df, p)
    frac = (p["bracket_atr"] * _atr_pine(bars_df, ATR_LEN) / bars_df["close"]).where(pd.Series(le | se, index=bars_df.index))
    return {"sl_stop": frac.shift(1), "tp_stop": frac.shift(1)}


def portfolio_kwargs(**params):
    return {}
