"""Close-to-close slope regimes, daily bars: a 20-bar slope over the threshold is long and under minus the threshold is short; the close crossing the SMA 50 either way closes; reversing.
Port of FMZ strategy #452712 "Dynamic Market Regime Identification Strategy Based on Linear Regression Slope" (Minha estratégia (linear slope regime)).

FMZ source id: 452712

Source
    https://www.fmz.com/strategy/452712 (PineScript v5, FMZ last modified 2024-05-28 13:51:31).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 84-122), slope (close - close[20]) / 20; threshold 0.1 (price units); SMA 50; margins 100 / 100
    slope > 0.1 -> entry Long;  slope < -0.1 -> entry Short;  crossover or crossunder(close, sma50) -> close Long, close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The 0.1 threshold is a price amount per bar; it is read against BTC near 42000 like other price
      units (#440456): the port tests the slope as a fraction of the close, 0.1 / 42000. Both entries
      are states (ignored while held). The entries are called before the closes: on an SMA cross a
      held trade on the regime's side is closed (its entry is ignored as held) and re-entered on a
      later bar, while an opposite regime reverses and the close then finds the trade reversed.
      REVERSAL INTENDED. The margin settings are sizing. FREQ = "1D" from the backtest header (broker
      days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the price-unit threshold as a fraction of 42000.
    2 generic: PASS, slope regimes with SMA-cross exits.
    3 crypto-exchange-only: no (spot pair in the header only (the source sends shorts as written)).
    4 signals only: the margin settings stored.
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

NAME = "fmz_452712_close_slope_regime_sma50_cross_exit_reversal"
FAMILY = "momentum_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "slope_len": [20, 10],
    "sma_len": [50, 100],
    "thr_frac": [2.38e-06, 0.001],
}
DEFAULT_PARAMS = {"slope_len": 20, "sma_len": 50, "thr_frac": 2.38e-06}


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
    c = bars_df["close"]
    n = int(p["slope_len"])
    slope = (c - c.shift(n)) / n / c
    t = float(p["thr_frac"])
    bull, bear = (slope > t).to_numpy(), (slope < -t).to_numpy()
    sma = c.rolling(int(p["sma_len"])).mean()
    c1 = c.shift(1)
    ex = (((c > sma) & (c1 <= sma.shift(1))) | ((c < sma) & (c1 >= sma.shift(1)))).to_numpy()
    m = len(c)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos = 0
    for i in range(m):
        cur = pos
        if bull[i] and cur != 1:
            cur = 1
        if bear[i] and cur != -1:
            cur = -1
        if ex[i] and pos != 0 and cur == pos:
            cur = 0                           # closes the trade held into the bar, if not reversed
        if cur == 1 and pos != 1:
            le[i] = True
        elif cur == -1 and pos != -1:
            se[i] = True
        elif cur == 0 and pos == 1:
            lx[i] = True
        elif cur == 0 and pos == -1:
            sx[i] = True
        pos = cur
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
