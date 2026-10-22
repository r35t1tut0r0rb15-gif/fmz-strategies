"""SMA 9 / 14 crossings from flat, daily bars, long only: a cross up goes long; a cross down, or a bar whose low reaches 10 % under the fill price, closes at the next open.
Port of FMZ strategy #445821 "Dual Moving Average Crossover with Optimized Stop Loss Strategy" (SMA Crossover Strategy with Customized Stop Loss (Long Only)).

FMZ source id: 445821

Source
    https://www.fmz.com/strategy/445821 (PineScript v4, FMZ last modified 2024-03-22 14:53:59).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 197-232), SMA 9 / 14; stop multiplier 0.1 of the average price (bar-close test); start 2022-01-01
    crossover(fast, slow) and position_size == 0 -> entry Buy;  crossunder(fast, slow) or low <= avg x (1 - 0.1) -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop is not an order: the bar's low is compared with 90 % of the average price at the bar
      close and strategy.close fills at the next open; the port runs that test against the fill (the
      next open after the signal) from the fill bar on. Before a fill the average price is na and the
      test is false. The 2022 start date is dropped (the data window decides). Long only. No sizing
      code. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the low test against the fill price at the close.
    2 generic: PASS, SMA crossings with a 10 % low test.
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

NAME = "fmz_445821_sma9_14_cross_low_10pct_close_long"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [9, 5],
    "stop_mult": [0.1, 0.05],
}
DEFAULT_PARAMS = {"fast": 9, "slow": 14, "stop_mult": 0.1}


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
    o, lo, c = bars_df["open"], bars_df["low"], bars_df["close"]
    f = c.rolling(int(p["fast"])).mean()
    s = c.rolling(int(p["slow"])).mean()
    f1, s1 = f.shift(1), s.shift(1)
    go = ((f > s) & (f1 <= s1)).to_numpy()
    xd = ((f < s) & (f1 >= s1)).to_numpy()
    ov, lv = o.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    k = 1.0 - float(p["stop_mult"])
    m = len(ov)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    held, fp = False, np.nan
    for i in range(m):
        if not held and go[i]:
            le[i] = True
            fp = ov[i + 1] if i + 1 < m else np.nan   # the fill: the next bar's open
        elif held and (xd[i] or lv[i] <= fp * k):
            lx[i] = True
        held = (held and not lx[i]) or le[i]
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
