"""Inverse Fisher transform of RSI 5, broker days: the transform of 10 x (RSI 5 - 50) (which saturates near +-1) crossing
above 0.8 goes long; crossing under the boolean "below -0.8" (read as 1 / 0, as written) goes short; always in once
started.
Port of FMZ strategy #432783 "逆向费希尔RSI平均真实范围多时间框架策略Inverse-Fisher-RSI-Moving-Average-Multi-Timeframe-Strategy" (Inverse Fisher RSI-MTF2).

FMZ source id: 432783

Source
    https://www.fmz.com/strategy/432783 (PineScript v4, FMZ last modified 2023-11-21 14:45:28).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 113-142), RSI 5, smoothing 1, timeframe 1440 (= the daily chart)
    v = IF(wma(0.1 x (rsi(close, 5) - 50), 1) x 100), IF(x) = (e^2x - 1) / (e^2x + 1)
    crossover(v, 0.8) -> entry long;  crossunder(v, b) with b = v < -0.8 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The security resolution "1440" minutes is the daily chart's own: no other timeframe is read.
      wma(x, 1) is x, so v = tanh(10 x (rsi - 50)), close to +-1 except right at RSI 50.
    * AS WRITTEN: the short trigger crosses v under the boolean b (v < -0.8), read as 1 when true and
      0 when false; it fires when v drops from at or above 0 to below -0.8. Listed with the as-written
      ports (the evident intent is a cross under -0.8).
    * strategy.entry reverses: REVERSAL INTENDED. Daily bars are broker days (17:00 America/New_York),
      stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, a transformed RSI against fixed levels.
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

NAME = "fmz_432783_inverse_fisher_rsi_as_written"
FAMILY = "rsi_oscillator"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_len": [5, 9],
    "scale": [10.0, 0.1],
}
DEFAULT_PARAMS = {"rsi_len": 5, "scale": 10.0, "level": 0.8}


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


def _rsi(x, n):
    d = x.diff()
    up = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    return 100 - 100 / (1 + up / dn)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    v = np.tanh(float(p["scale"]) * (_rsi(c, int(p["rsi_len"])) - 50))   # IF(wma_RSI) = tanh(10 x (rsi - 50)) as written
    z = float(p["level"])
    b = (v < -z).astype(float)
    x = ((v > z) & (v.shift(1) <= z)).to_numpy()
    y = ((v < b) & (v.shift(1) >= b.shift(1))).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if x[i]:
            pos = 1
        if y[i]:
            pos = -1
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    se = (tgt == -1) & (prev != -1)
    false = np.zeros(m, dtype=bool)
    return tuple(pd.Series(a, index=bars_df.index) for a in (le, false, se, false.copy()))


def portfolio_kwargs(**params):
    return {}
