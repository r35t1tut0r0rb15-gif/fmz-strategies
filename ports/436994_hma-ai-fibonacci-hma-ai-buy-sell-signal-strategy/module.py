"""Hull average 21 / 233 crossings, broker days: the HMA 21 crossing over the HMA 233 goes long, crossing under goes short; reversing.
Port of FMZ strategy #436994 "基于斐波那契HMA的AI买卖信号策略Fibonacci-HMA-AI-Buy-Sell-Signal-Strategy" (AI Fibonacci HMA Strategy | Buy / Sell Indicator).

FMZ source id: 436994

Source
    https://www.fmz.com/strategy/436994 (PineScript v4, FMZ last modified 2023-12-29 11:24:34).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 86-114), HMA 21, 233 (HMA 377 plotted only)
    hma21 > hma233 and hma21[1] < hma233[1] (nz to the current value) -> entry Buy;  hma21 < hma233 and hma21[1] > hma233[1] -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * hma(n) = wma(2 wma(close, n / 2) - wma(close, n), round(sqrt(n))) with integer n / 2. The previous
      values fall back to the current ones (nz), so no crossing fires on the first bar. A crossing
      needs a strict change of side (an exact tie on the previous bar is no crossing), as written. The
      HMA 377 is plotted only. REVERSAL INTENDED. No sizing code. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, average crossing.
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

NAME = "fmz_436994_hma_21_233_cross"
FAMILY = "ma_cross"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [21, 34],
    "slow": [233, 144],
}
DEFAULT_PARAMS = {"fast": 21, "slow": 233}


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


def _wma(x, n):
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda v: np.dot(v, w) / w.sum(), raw=True)


def _hma(src, n):
    return _wma(2 * _wma(src, n // 2) - _wma(src, n), int(round(np.sqrt(n))))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    f = _hma(c, int(p["fast"]))
    s = _hma(c, int(p["slow"]))
    f1 = f.shift(1).where(f.shift(1).notna(), f)
    s1 = s.shift(1).where(s.shift(1).notna(), s)
    up = (f > s) & (f1 < s1)
    dn = (f < s) & (f1 > s1)
    false = pd.Series(False, index=bars_df.index)
    return up, false, dn, false.copy()


def portfolio_kwargs(**params):
    return {}
