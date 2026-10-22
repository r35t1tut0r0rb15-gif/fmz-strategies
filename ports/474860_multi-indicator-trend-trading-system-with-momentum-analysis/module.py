"""SMA 200 side with stochastic-RSI and MACD states, daily bars: over the SMA 200 with %K over %D and MACD over its signal it goes long, the mirror goes short; a close under the SMA 50 closes a long, over it closes a short; reversing.
Port of FMZ strategy #474860 "Multi Indicator Trend Trading System with Momentum Analysis Strategy" (RSI and MACD by Karthik).

FMZ source id: 474860

Source
    https://www.fmz.com/strategy/474860 (PineScript v5, FMZ last modified 2024-12-12 15:53:21).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 134-246), SMA 50 / 200; RSI 14; "stochastic RSI" ta.stoch(rsi, rsi, 14, 3) as written; MACD 12 / 26 / 9 (constants)
    K = ta.stoch(rsi, rsi, 14, 3);  close > sma200 and K > D and macd > signal -> entry Long;  close < sma200 and K < D and macd < signal -> entry Short;  close < sma50 -> close Long;  close > sma50 -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.stoch(source, high, low, length) is called with (rsi, rsi, 14, 3): the "low" is the constant
      14 and the length 3, so K = 100 x (rsi - 14) / (highest(rsi, 3) - 14), as written; D is its SMA 3.
      The closes are bar-close tests (when=); a close acts only on the side held into the bar and not
      reversed on it (#437773); a loop follows the position. The lastSignal block only drives plots.
      REVERSAL INTENDED. No sizing code. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, trend / momentum states with SMA 50 closes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: fixed qty 1 stored, not ported.
    5 ranges declared: GRID below (1 trial), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_474860_sma200_stochrsi_as_written_macd_state_sma50_exit_reversal"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {}
DEFAULT_PARAMS = {}


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
    c = bars_df["close"]
    s50, s200 = c.rolling(50).mean(), c.rolling(200).mean()
    r = _rsi(c, 14)
    k = 100 * (r - 14.0) / (r.rolling(3).max() - 14.0)   # ta.stoch(rsi, rsi, 14, 3): low = 14, length 3
    d = k.rolling(3).mean()
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    buy = ((c > s200) & (k > d) & (macd > sig)).to_numpy()
    sell = ((c < s200) & (k < d) & (macd < sig)).to_numpy()
    xb = (c < s50).to_numpy()
    xs = (c > s50).to_numpy()
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, nxt = 0, 0
    for i in range(m):
        pos = nxt
        if buy[i] and nxt != 1:
            le[i], nxt = True, 1
        if sell[i] and nxt != -1:
            se[i], nxt = True, -1
        if xb[i] and pos == 1 and nxt == 1:
            lx[i], nxt = True, 0
        if xs[i] and pos == -1 and nxt == -1:
            sx[i], nxt = True, 0
    ix = bars_df.index
    return tuple(pd.Series(z, index=ix) for z in (le, lx, se, sx))


def portfolio_kwargs(**params):
    return {}
