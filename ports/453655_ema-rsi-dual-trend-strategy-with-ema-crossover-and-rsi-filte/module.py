"""EMA 9 / 21 crossings confirmed by the RSI 14 and the MACD side, daily bars: the cross up with the RSI under 70 and the MACD over its signal goes long, the cross down with the RSI over 30 and the MACD under goes short; reversing.
Port of FMZ strategy #453655 "EMA交叉与RSI过滤的双重趋势策略-Dual-Trend-Strategy-with-EMA-Crossover-and-RSI-Filter" (15 Dakikalık Göstergelerle Strateji (15m Strat)).

FMZ source id: 453655

Source
    https://www.fmz.com/strategy/453655 (PineScript v5, FMZ last modified 2024-06-07 15:29:57).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 95-135), EMA 9 / 21; RSI 14, levels 70 / 30; MACD 12 / 26 / 9
    crossover(ema9, ema21) and rsi < 70 and macd > signal -> entry Long;  crossunder and rsi > 30 and macd < signal -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * There is no exit: positions end at the opposite entry. The title's 15 minutes is not the header's
      period. REVERSAL INTENDED. No sizing code. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, confirmed EMA crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_453655_ema9_21_cross_rsi_macd_confirm_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "short_len": [9, 5],
    "long_len": [21, 50],
    "rsi_len": [14, 7],
}
DEFAULT_PARAMS = {"short_len": 9, "long_len": 21, "rsi_len": 14, "ob": 70.0, "os": 30.0}


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
    a = c.ewm(span=int(p["short_len"]), adjust=False).mean()
    b = c.ewm(span=int(p["long_len"]), adjust=False).mean()
    r = _rsi(c, int(p["rsi_len"]))
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    le = (a > b) & (a.shift(1) <= b.shift(1)) & (r < float(p["ob"])) & (macd > sig)
    se = (a < b) & (a.shift(1) >= b.shift(1)) & (r > float(p["os"])) & (macd < sig)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
