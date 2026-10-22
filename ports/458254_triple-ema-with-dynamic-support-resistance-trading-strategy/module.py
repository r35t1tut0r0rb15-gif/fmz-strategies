"""EMA 10 / 20 crossings on the side of the EMA 50 and of the last 20-bar closing extreme, daily bars: the cross up with the close over the EMA 50 and over the last 20-bar closing low goes long, the mirror goes short, each with a 1 % stop and 2 % target; reversing.
Port of FMZ strategy #458254 "Triple EMA with Dynamic Support Resistance Trading Strategy" (3 EMA Strategy with Support/Resistance).

FMZ source id: 458254

Source
    https://www.fmz.com/strategy/458254 (PineScript v5, FMZ last modified 2024-07-31 11:58:57).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 182-243), EMA 10 / 20 / 50; support / resistance = the last close that was the 20-bar closing low / high (kept); stop 1 %, target 2 % of the signal close
    crossover(ema10, ema20) and close > ema50 and close > support -> entry Long + exit(stop = close x 0.99, limit = close x 1.02)
    crossunder and close < ema50 and close < resistance -> entry Short + exit(stop = close x 1.01, limit = close x 0.98)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The support and resistance levels are var values set when the close is the 20-bar closing low /
      high (na before the first). The bracket is sent once on the signal bar from its close: ported as
      the fixed fractions 0.01 / 0.02 of the fill. REVERSAL INTENDED. Stop module: portfolio_kwargs {}
      (driver D4). Stops on daily bars: mark coarse_bar_stop. No sizing code. FREQ = "1D" from the
      backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the percent bracket as fixed fractions.
    2 generic: PASS, EMA crossings with trend and level filters.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_458254_ema10_20_cross_ema50_close_extreme_filter_pct_bracket_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "short_len": [10, 5],
    "mid_len": [20, 30],
    "sl_pct": [0.01, 0.03],
}
DEFAULT_PARAMS = {"short_len": 10, "mid_len": 20, "long_len": 50, "sl_pct": 0.01, "tp_pct": 0.02}


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


def _kept(x):
    """A Pine var set only on some bars: the last value set, na before the first."""
    v = x.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    last = np.nan
    for i in range(len(v)):
        if not np.isnan(v[i]):
            last = v[i]
        out[i] = last
    return pd.Series(out, index=x.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    es, em, el = (c.ewm(span=int(p[k]), adjust=False).mean() for k in ("short_len", "mid_len", "long_len"))
    sup = _kept(c.where(c.rolling(20).min() == c))
    res = _kept(c.where(c.rolling(20).max() == c))
    le = (es > em) & (es.shift(1) <= em.shift(1)) & (c > el) & (c > sup)
    se = (es < em) & (es.shift(1) >= em.shift(1)) & (c < el) & (c < res)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_pct"]), "tp_stop": float(p["tp_pct"])}


def portfolio_kwargs(**params):
    return {}
