"""Super Trend Daily 2.0 BF: a fast SuperTrend (ATR 2 x 1.5) turning up while the 30-bar ROC is
moving (|EMA of ROC| > 3 %) goes long; a second SuperTrend (ATR 3 x 1.3) turning down while the
76-bar ROC is moving goes short. Fixed stops: 5 % under a long's entry, 6 % over a short's.
Port of FMZ strategy #365892 "Super Trend Daily 2.0 BF".

Source
    https://www.fmz.com/strategy/365892 (PineScript v4, FMZ last modified 2022-05-26 16:48:33).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 102-233), ST L 2 x 1.5, ST S 3 x 1.3, ROC 30 / 76 (6 %),
stop type Fixed 5 % / 6 %
    long  = dirl turns 1 and |ema(roc(30), 15)| > 3   -> entry "L"
    short = dirs turns -1 and |ema(roc(76), 38)| > 3  -> entry "S"
    exit L: stop = avg price * 0.95;  exit S: stop = avg price * 1.06

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stops are fixed fractions of the entry price: stops() returns sl_stop 0.05 for long
      entries and 0.06 for short ones, shifted one bar inside stops(); vbt applies them from the
      fill bar, while the source places them one bar later (since_longEntry > 0).
    * Both entries on one bar: the later order (short) wins, as Pine fills them in order.
    * Pine v4 integer division: ROC EMA lengths 30 / 2 = 15 and 76 / 2 = 38. testPeriod() is true.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "10min" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_365892_dual_supertrend_roc_filter"
FAMILY = "supertrend"  # proposed 2026-10-07, user to confirm
FREQ = "10min"  # backtest header period: 10m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "roc_len_l": [15, 30],
    "roc_len_s": [38, 76],
    "sl_long": [0.03, 0.05],
}
DEFAULT_PARAMS = {"atr_l": 2, "mult_l": 1.5, "atr_s": 3, "mult_s": 1.3, "roc_len_l": 30, "roc_len_s": 76,
                  "roc_pct": 6.0, "sl_long": 0.05, "sl_short": 0.06}


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


def _st_classic(bars, src, period, mult):
    """Classic (KivancOzbilgic) SuperTrend trend: up/dn ratchet on close[1]; trend starts at 1."""
    s = np.asarray(src, dtype=float)
    c = bars["close"].to_numpy(dtype=float)
    atr = _atr_pine(bars, period).to_numpy()
    m = len(c)
    trend = np.ones(m)
    up_prev = dn_prev = np.nan
    for i in range(m):
        up, dn = s[i] - mult * atr[i], s[i] + mult * atr[i]
        up_a = up if np.isnan(up_prev) else up_prev
        dn_a = dn if np.isnan(dn_prev) else dn_prev
        if i and c[i - 1] > up_a:
            up = max(up, up_a)
        if i and c[i - 1] < dn_a:
            dn = min(dn, dn_a)
        t = trend[i - 1] if i else 1.0
        trend[i] = 1.0 if (t == -1 and c[i] > dn_a) else (-1.0 if (t == 1 and c[i] < up_a) else t)
        up_prev, dn_prev = up, dn
    return trend


def _signals(bars_df, p):
    src = (bars_df["high"] + bars_df["low"]) / 2
    tl = _st_classic(bars_df, src, int(p["atr_l"]), float(p["mult_l"]))
    ts = _st_classic(bars_df, src, int(p["atr_s"]), float(p["mult_s"]))
    c = bars_df["close"]

    def moving(n):
        roc = 100 * (c - c.shift(n)) / c.shift(n)
        e = roc.ewm(span=n // 2, adjust=False).mean()
        return ((e > p["roc_pct"] / 2) | (e < -p["roc_pct"] / 2)).to_numpy()

    lag = lambda a: np.concatenate([[np.nan], a[:-1]])
    long_ = (tl == 1) & (lag(tl) == -1) & moving(int(p["roc_len_l"]))
    short = (ts == -1) & (lag(ts) == 1) & moving(int(p["roc_len_s"]))
    return long_ & ~short, short


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
    sl = pd.Series(np.where(le, p["sl_long"], np.where(se, p["sl_short"], np.nan)), index=bars_df.index)
    return {"sl_stop": sl.shift(1)}


def portfolio_kwargs(**params):
    return {}
