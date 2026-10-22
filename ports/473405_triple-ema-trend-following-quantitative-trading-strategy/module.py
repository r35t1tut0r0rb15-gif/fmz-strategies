"""EMA 10 / 30 / 130 trend crossings, daily bars, long only: EMA 10 crossing over EMA 30 with both slower EMAs rising, or over EMA 130 with it rising, buys; EMA 10 crossing under EMA 30 sells.
Port of FMZ strategy #473405 "Triple EMA Trend Following Quantitative Trading Strategy" (Estrategia de Largo con Medias Móviles).

FMZ source id: 473405

Source
    https://www.fmz.com/strategy/473405 (PineScript v5, FMZ last modified 2024-11-29 16:54:41).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 98-143), EMA 10 / 30 / 130; one-bar slopes
    (crossover(f, m) and m rising and s rising) or (crossover(f, s) and s rising) -> entry Comprar;  crossunder(f, m) -> close Comprar

Interpretation choices (Pine rules in SURVEY_README.md)
    * The close acts only on a long held into the bar (#437773): a bar with both an entry and the close
      sends the entry from flat, and closes a held long. A loop follows that. Long only. No sizing code.
      FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA crossings with slope filters.
    3 crypto-exchange-only: no (exchange pair in the header only).
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

NAME = "fmz_473405_ema10_30_130_slope_cross_long"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [10, 5],
    "mid": [30, 50],
    "slow": [130, 200],
}
DEFAULT_PARAMS = {"fast": 10, "mid": 30, "slow": 130}


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


def _x(a, b):
    return (a > b) & (a.shift(1) <= b.shift(1))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    f, md, s = (c.ewm(span=int(p[k]), adjust=False).mean() for k in ("fast", "mid", "slow"))
    s_up, m_up = s > s.shift(1), md > md.shift(1)
    go = ((_x(f, md) & m_up & s_up) | (_x(f, s) & s_up)).to_numpy()
    out = _x(md, f).to_numpy()
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, nxt = 0, 0
    for i in range(m):
        pos = nxt
        if go[i] and pos == 0:
            le[i], nxt = True, 1
        if out[i] and pos == 1:
            lx[i], nxt = True, 0
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
