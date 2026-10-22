"""SMA 10 / 30 cross-ups with a bullish MACD, or an oversold double bottom, daily bars, long only: either buys; a close at the 20-bar closing high with a bearish MACD, or an overbought double top / head-and-shoulders (unless the RSI is under 30), sells.
Port of FMZ strategy #471702 "Multi Period Technical Analysis and Market Sentiment Trading Strategy" (XAUUSD SMA with MACD & Market Sentiment + Chart Patterns).

FMZ source id: 471702

Source
    https://www.fmz.com/strategy/471702 (PineScript v5, FMZ last modified 2024-11-12 15:52:16).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 109-194), SMA 10 / 30; MACD 12 / 26 / 9; highest(close, 20); RSI 14, 70 / 30; double top / bottom = the 50-bar extreme equal to close and close[25]; H&S from three 20-bar highs; New York session always true
    (crossover(sma10, sma30) and macd > signal) or (double bottom and rsi < 30) -> entry Buy
    (close >= highest(close, 20) and macd < signal) or ((double top or H&S) and rsi > 70 and not (long and rsi < 30)) -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * `a or b and not c` reads as `a or (b and not c)`, as Pine does. The pattern tests use exact
      equality of closes, as written. The New York session flag is set to true, and the short-side
      close never acts (no short is opened). The entry is called before the close; the close acts only
      on a long held into the bar. The title names XAUUSD; the rules are generic. Long only. No sizing
      code. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SMA crossings and chart patterns with resistance exits.
    3 crypto-exchange-only: no (exchange pair in the header only (XAUUSD named in the title)).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used (the flag is always true).
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_471702_sma10_30_cross_double_bottom_resistance_pattern_exit_long"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "short_len": [10, 5],
    "long_len": [30, 50],
}
DEFAULT_PARAMS = {"short_len": 10, "long_len": 30, "res_len": 20, "rsi_len": 14}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def _rma(x, n):
    """Wilder smoothing as Pine's rma: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def _rsi(c, n):
    d = c.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    return 100 - 100 / (1 + up / dn)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    s, l = c.rolling(int(p["short_len"])).mean(), c.rolling(int(p["long_len"])).mean()
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    r = _rsi(c, int(p["rsi_len"]))
    hi50, lo50 = c.rolling(50).max(), c.rolling(50).min()
    dtop = (hi50 == c.shift(25)) & (hi50 == c)
    dbot = (lo50 == c.shift(25)) & (lo50 == c)
    h20 = c.rolling(20).max()
    hs = (h20.shift(40) < h20.shift(20)) & (h20 < h20.shift(20)) & (h20.shift(40) == h20)
    buy = (((s > l) & (s.shift(1) <= l.shift(1)) & (macd > sig)) | (dbot & (r < 30))).to_numpy()
    sell_a = ((c >= c.rolling(int(p["res_len"])).max()) & (macd < sig)).to_numpy()
    sell_b = ((dtop | hs) & (r > 70)).to_numpy()
    rv = r.to_numpy()
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if buy[i] and pos == 0:
            le[i], pos = True, 1
        elif pos == 1 and (sell_a[i] or (sell_b[i] and not (rv[i] < 30))):
            lx[i], pos = True, 0                 # the close acts only on a long held into the bar
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
