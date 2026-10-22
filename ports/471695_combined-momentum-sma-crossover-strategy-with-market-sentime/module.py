"""SMA 10 / 30 cross-ups with the MACD over its signal, daily bars, long only: the cross up with a bullish MACD buys; a close at the 20-bar closing high with the MACD under its signal sells, unless the RSI is under 30.
Port of FMZ strategy #471695 "Combined Momentum SMA Crossover Strategy with Market Sentiment and Resistance Level Optimization System" (XAUUSD SMA with MACD & Market Sentiment (Enhanced RR)).

FMZ source id: 471695

Source
    https://www.fmz.com/strategy/471695 (PineScript v5, FMZ last modified 2024-11-12 15:10:12).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 90-154), SMA 10 / 30; MACD 12 / 26 / 9; resistance = highest(close, 20) (current bar included); RSI 14, levels 70 / 30
    crossover(sma10, sma30) and macd > signal -> entry Buy;  close >= highest(close, 20) and macd < signal and not (long and rsi < 30) -> close Buy
    short and rsi > 70 -> close Buy (never: no short is opened)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "close early" test needs a short position, which the script never opens, so it never acts.
      The resistance includes the current close, so the exit means a close at a 20-bar closing high.
      The entry is called before the close; the close acts only on a long held into the bar. The title
      names XAUUSD; the rules are generic. Long only. No sizing code. FREQ = "1D" from the backtest
      header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SMA crossings with a resistance exit.
    3 crypto-exchange-only: no (exchange pair in the header only (XAUUSD named in the title)).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_471695_sma10_30_cross_macd_exit_at_closing_high_long"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "short_len": [10, 5],
    "long_len": [30, 50],
    "res_len": [20, 50],
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
    r = _rsi(c, int(p["rsi_len"])).to_numpy()
    buy = ((s > l) & (s.shift(1) <= l.shift(1)) & (macd > sig)).to_numpy()
    sell = ((c >= c.rolling(int(p["res_len"])).max()) & (macd < sig)).to_numpy()
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if buy[i] and pos == 0:
            le[i], pos = True, 1
        elif sell[i] and pos == 1 and not (r[i] < 30):
            lx[i], pos = True, 0                 # the close acts only on a long held into the bar
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
