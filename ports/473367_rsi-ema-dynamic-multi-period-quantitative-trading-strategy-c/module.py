"""RSI 14 turns back from extremes with the EMA 400 trend, 2-day bars: an RSI that was over 70 two bars ago and is now under it, with the close over the EMA 400, goes long; the oversold mirror under the EMA goes short; reversing. The 1 % bracket re-sent every bar from that bar's close is not ported (pending).
Port of FMZ strategy #473367 "RSI与EMA结合的动态多周期量化交易策略-Dynamic-Multi-Period-Quantitative-Trading-Strategy-Combining-RSI-and-EMA" (RSI BUY/SELL + EMA + SLTP by rcpislr).

FMZ source id: 473367

Source
    https://www.fmz.com/strategy/473367 (PineScript v5, FMZ last modified 2024-11-29 15:35:11).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 94-137), RSI 14, 70 / 30; EMA 400 filter on; stop / target 1 % of the current close (every bar)
    rsi[2] > 70 and rsi < 70 and close > ema -> entry Long;  rsi[2] < 30 and rsi > 30 and close < ema -> entry Short;  long: exit(stop = close x 0.99, limit = close x 1.01) every bar;  short: mirror

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is re-sent on every bar from that bar's close, so its levels move after entry: a
      level re-set every bar is not ported (as #438034, mark trailing_stop_pending). Positions end at
      the opposite entry until then. As written, the long fires on an overbought turn (rsi[2] > 70,
      now under 70). REVERSAL INTENDED. No sizing code. FREQ = "2D" from the backtest header (blocks of
      2 broker days, as #429148).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI turns from extremes with an EMA filter; per-bar bracket described (pending).
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent bracket stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_473367_rsi_extreme_turn_ema400_reversal_bracket_pending"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2D"  # backtest header period: 2d (blocks of 2 broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_period": [400, 200],
    "rsi_period": [14, 7],
}
DEFAULT_PARAMS = {"ema_period": 400, "rsi_period": 14, "days": 2}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _multiday(raw_1m_df, days):
    """Blocks of `days` broker days counted from 1970-01-01, each stamped with its first minute."""
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    key = np.asarray((broker_day(df.index) - pd.Timestamp("1970-01-01")).days // days)
    bars = df.groupby(key).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(key).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    p = {**DEFAULT_PARAMS, **params}
    return _multiday(raw_1m_df, int(p["days"]))


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
    r = _rsi(c, int(p["rsi_period"]))
    e = c.ewm(span=int(p["ema_period"]), adjust=False).mean()
    le = (r.shift(2) > 70) & (r < 70) & (c > e)
    se = (r.shift(2) < 30) & (r > 30) & (c < e)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
