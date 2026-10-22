"""Hull MA 20 crossings across time frames, 1-hour bars: the Hull MA of 25-minute bars crossing over the Hull MA of 75-minute bars goes long, crossing under goes short; reversing.
Port of FMZ strategy #458047 "多周期Hull移动平均线交叉策略-Multi-Timeframe-Hull-Moving-Average-Crossover-Strategy" (Hull v2 Strategy (V2 HMA, 25 / 75-minute Hull averages)).

FMZ source id: 458047

Source
    https://www.fmz.com/strategy/458047 (PineScript v5, FMZ last modified 2024-07-29 14:44:25).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 194-235), Hull MA 20 on '25', '75' and '125' minutes (the 125-minute one plotted only)
    hull_25 = security('25', hma20);  hull_75 = security('75', hma20);  crossover(hull_25, hull_75) -> entry Long;  crossunder -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Both requests have no lookahead: each 1-hour bar reads the Hull value of the last 25-minute and
      the last 75-minute bar completed by its close (the 25-minute one as #436765, the 75-minute one as
      #440503). The odd-minute bars are built from the minutes and anchored at each UTC day's start
      (the last bar of a day is shorter), as TradingView anchors intraday resolutions to the session
      start. The Hull MA is wma(2 wma(n / 2) - wma(n), round(sqrt(n))). There is no exit: positions end
      at the opposite entry. REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the odd-minute values from completed bars.
    2 generic: PASS, Hull MA crossings across time frames.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_458047_hull20_25m_75m_cross_reversal"
FAMILY = "hull_ma"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 10],
}
DEFAULT_PARAMS = {"length": 20, "tf_fast": 25, "tf_slow": 75}


def _wma(x, n):
    n = int(n)
    out = pd.Series(0.0, index=x.index)
    for k in range(n):
        out = out + (n - k) * x.shift(k)
    return out / (n * (n + 1) / 2)


def _hull(x, n):
    return _wma(2 * _wma(x, n // 2) - _wma(x, n), int(round(np.sqrt(n))))


def _day_anchored(df, minutes):
    """Bars of `minutes` anchored at each UTC day's start (the day's last bar may be shorter)."""
    day = df.index.floor("1D")
    off = ((df.index - day) // pd.Timedelta(minutes=minutes)) * pd.Timedelta(minutes=minutes)
    start = day + off
    agg = df.groupby(start).agg({"close": "last"})
    end = np.minimum((agg.index + pd.Timedelta(minutes=minutes)).asi8,
                     (agg.index.floor("1D") + pd.Timedelta(days=1)).asi8)
    return agg["close"], end


def precompute(raw_1m_df, symbol_key, **params):
    p = {**DEFAULT_PARAMS, **params}
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    agg = {"open": "first", "high": "max", "low": "min", "close": "last"}
    bars = df.resample(FREQ, label="left", closed="left").agg(agg).dropna(how="all")
    done = (bars.index + pd.Timedelta(hours=1)).asi8
    n = int(p["length"])
    for col, tf in (("hull_fast", int(p["tf_fast"])), ("hull_slow", int(p["tf_slow"]))):
        closes, end = _day_anchored(df, tf)
        hv = _hull(closes, n).to_numpy()
        k = np.searchsorted(end, done, side="right") - 1      # last odd-minute bar closed by the chart close
        ok = k >= 0
        bars[col] = np.where(ok, hv[np.where(ok, k, 0)], np.nan)
    return bars


def simulate(bars_df, **params):
    a, b = bars_df["hull_fast"], bars_df["hull_slow"]
    le = (a > b) & (a.shift(1) <= b.shift(1))
    se = (a < b) & (a.shift(1) >= b.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
