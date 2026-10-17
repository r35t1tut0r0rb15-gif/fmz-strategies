"""Fast / slow ATR trailing-line crosses, broker days, long only: the fast line (0.5 x ATR 5) crossing above the slow line
(3 x ATR 10) goes long, crossing below closes it.
Port of FMZ strategy #434976 "动态ATR追踪止损策略Dynamic-ATR-Trailing-Stop-Loss-Strategy" (ATR Trailing Stop Strategy by ceyhun).

FMZ source id: 434976

Source
    https://www.fmz.com/strategy/434976 (PineScript v4, FMZ last modified 2023-12-11 14:24:18).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 110-161), source close; fast ATR 5 x 0.5, slow ATR 10 x 3
    trail_n = Vervoort trailing line of close with SL_n = AF_n x atr(AP_n);  crossover(trail1, trail2) -> entry long;  crossunder(trail1, trail2) -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * Both lines are signal lines on closes (no broker stop). The bar colours are drawing only.
      Long only. Daily bars are broker days (17:00 America/New_York), stamped with their first
      minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, ATR trailing lines.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG434976 (2 members, best partner #440561, Jaccard 0.852); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_434976_dual_atr_trail_cross_long"
FAMILY = "volatility_stop_cross"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast_mult": [0.5, 1.0],
    "slow_mult": [3.0, 2.0],
}
DEFAULT_PARAMS = {"fast_len": 5, "fast_mult": 0.5, "slow_len": 10, "slow_mult": 3.0}


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


def _trail(cv, nl):
    m = len(cv)
    ts = np.full(m, np.nan)
    for i in range(m):
        t1 = ts[i - 1] if i > 0 and not np.isnan(ts[i - 1]) else 0.0
        cp = cv[i - 1] if i > 0 else np.nan
        if cv[i] > t1 and cp > t1:
            ts[i] = max(t1, cv[i] - nl[i])
        elif cv[i] < t1 and cp < t1:
            ts[i] = min(t1, cv[i] + nl[i])
        else:
            ts[i] = cv[i] - nl[i] if cv[i] > t1 else cv[i] + nl[i]
    return ts


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    tr.iloc[0] = np.nan
    atr = lambda n: tr.ewm(alpha=1 / n, adjust=False).mean().to_numpy()  # noqa: E731
    cv = c.to_numpy(dtype=float)
    t1 = _trail(cv, float(p["fast_mult"]) * atr(int(p["fast_len"])))
    t2 = _trail(cv, float(p["slow_mult"]) * atr(int(p["slow_len"])))
    a1, b1 = np.concatenate(([np.nan], t1[:-1])), np.concatenate(([np.nan], t2[:-1]))
    with np.errstate(invalid="ignore"):
        le = (t1 > t2) & (a1 <= b1)
        lx = (t1 < t2) & (a1 >= b1)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
