"""EMA 5 / 20 crossings with an RSI 14 side filter, daily bars: the cross up with the RSI over 50 goes long, the cross down with the RSI under 50 goes short; reversing.
Port of FMZ strategy #455361 "Multi Momentum Linear Regression Crossover Strategy" (Estrategia de Momentum (EMA 5 / 20 with RSI)).

FMZ source id: 455361

Source
    https://www.fmz.com/strategy/455361 (PineScript v5, FMZ last modified 2024-06-28 15:21:38).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 212-265), EMA 5 / 20; RSI 14 vs 50; linreg 100 channel plotted only
    crossover(ema5, ema20) and rsi > 50 -> entry Buy;  crossunder and rsi < 50 -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The regression channel is only plotted and the alerts carry no orders. There is no exit:
      positions end at the opposite entry. REVERSAL INTENDED. No sizing code. FREQ = "1D" from the
      backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA crossings with an RSI filter.
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

NAME = "fmz_455361_ema5_20_cross_rsi50_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [5, 9],
    "slow": [20, 50],
    "rsi_len": [14, 7],
}
DEFAULT_PARAMS = {"fast": 5, "slow": 20, "rsi_len": 14}


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
    a = c.ewm(span=int(p["fast"]), adjust=False).mean()
    b = c.ewm(span=int(p["slow"]), adjust=False).mean()
    r = _rsi(c, int(p["rsi_len"]))
    le = (a > b) & (a.shift(1) <= b.shift(1)) & (r > 50)
    se = (a < b) & (a.shift(1) >= b.shift(1)) & (r < 50)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
