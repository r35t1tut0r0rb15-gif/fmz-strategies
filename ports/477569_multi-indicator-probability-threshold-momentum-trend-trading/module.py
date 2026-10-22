"""Any of RSI 14 under 30, stochastic 14 under 20 or MACD over its signal, with the 20-bar close z-score over 0.5, goes long; any of RSI over 70, stochastic over 80 or MACD under its signal, with the z-score under -0.5, goes short; broker days; reversing.
Port of FMZ strategy #477569 "Multi Indicator Probability Threshold Momentum Trend Trading Strategy" (RSI-MACD-Stochastic Strategy).

FMZ source id: 477569

Source
    https://www.fmz.com/strategy/477569 (PineScript v5, FMZ last modified 2025-01-06 14:15:11).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 84-139), RSI 14; stochastic 14, D 3; MACD 12 / 26 / 9; z-score 20; thresholds 0.5 / -0.5
    (rsi < 30 or k < 20 or macd > signal) and z > 0.5 -> entry Buy;  (rsi > 70 or k > 80 or macd < signal) and z < -0.5 -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The tests are states, so entries repeat and are ignored on the held side; the z-score signs keep
      the two sides apart. ta.stdev is the population deviation. REVERSAL INTENDED. No sizing code. Daily
      bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from
      the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, oscillator votes with a z-score filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_477569_rsi_stoch_macd_vote_zscore20_reversal"
FAMILY = "zscore_momentum"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "lookback": [20, 50],
    "threshold": [0.5, 1.0],
}
DEFAULT_PARAMS = {"lookback": 20, "threshold": 0.5, "rsi_period": 14}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["rsi_period"])
    r = _rsi(c, n)
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    k = 100 * (c - ll) / (hh - ll).where(hh > ll)
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    w = int(p["lookback"])
    z = (c - c.rolling(w).mean()) / c.rolling(w).std(ddof=0)
    t = float(p["threshold"])
    le = ((r < 30) | (k < 20) | (macd > sig)) & (z > t)
    se = ((r > 70) | (k > 80) | (macd < sig)) & (z < -t)
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
