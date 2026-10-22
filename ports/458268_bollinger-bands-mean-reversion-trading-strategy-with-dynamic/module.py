"""Close crossings of the Bollinger 20 basis, daily bars, long only: the close crossing over the SMA 20 buys; the close crossing back under it, or a close more than 2 % under the fill, sells.
Port of FMZ strategy #458268 "Bollinger-Bands-Mean-Reversion-Trading-Strategy-with-Dynamic-Support-布林带均值回归交易策略与动态支撑" (Mean Reversion Strategy with Bollinger Bands).

FMZ source id: 458268

Source
    https://www.fmz.com/strategy/458268 (PineScript v5, FMZ last modified 2024-07-31 14:19:48).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 240-291), BB 20, 2 sd (bands plotted); stop: close under 98 % of the average price; no same-day buy and sell
    crossover(close, basis) and not the entry's day -> entry Long, remember the day
    (crossunder(close, basis) or long and close < avg x 0.98) and long and (another day or the drop) -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * On daily bars every bar is a different calendar day, so the same-day guards never block. The drop
      stop is a bar-close test against the fill price, filled at the next open, followed in a loop. The
      close acts only on a long held into the bar. Long only. No sizing code. FREQ = "1D" from the
      backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the stop is a close test against the fill.
    2 generic: PASS, mean-line crossings with a percent stop.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_458268_close_cross_sma20_drop_stop_close_test_long"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 50],
    "drop_pct": [0.02, 0.05],
}
DEFAULT_PARAMS = {"length": 20, "drop_pct": 0.02}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, c = bars_df["open"], bars_df["close"]
    basis = c.rolling(int(p["length"])).mean()
    xo = ((c > basis) & (c.shift(1) <= basis.shift(1))).to_numpy()
    xu = ((c < basis) & (c.shift(1) >= basis.shift(1))).to_numpy()
    ov, cv = o.to_numpy(dtype=float), c.to_numpy(dtype=float)
    dp = float(p["drop_pct"])
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, pend, entry = 0, 0, np.nan
    for i in range(m):
        if pend == 1:
            pos, entry = 1, ov[i]
        elif pend == 2:
            pos, entry = 0, np.nan
        pend = 0
        if xo[i] and pos == 0:
            le[i], pend = True, 1
        if pos == 1 and (xu[i] or cv[i] < entry * (1 - dp)):
            lx[i], pend = True, 2
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
