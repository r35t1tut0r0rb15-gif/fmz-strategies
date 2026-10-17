"""EMA 7 / 21 crosses, broker days: a cross up goes long, a cross down goes short (reversing); each trade carries a stop of
2500 ticks, re-expressed as an ATR multiple.
Port of FMZ strategy #434593 "EMA动量均线交叉策略EMA-Momentum-Moving-Average-Crossover-Strategy" (EMA_Crossover).

FMZ source id: 434593

Source
    https://www.fmz.com/strategy/434593 (PineScript v5, FMZ last modified 2023-12-07 17:00:52).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 140-170), EMA 7 / 21; quantity 1; stop 2500 ticks
    crossover(ema7, ema21) -> entry long;  crossunder -> entry short;  exit(loss = 2500) for each entry

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: 2500 ticks of 0.1 on daily BTC (250 USD) are about 0.2 x the daily Wilder ATR 14
      of the signal bar in 2023 (sl_atr, a fraction of the signal close shifted one bar inside
      stops(), re-based on the fill). Both exits share one id with different entries: read as one
      exit per entry.
    * strategy.entry reverses: REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). Stops
      on daily bars: mark coarse_bar_stop. Daily bars are broker days (17:00 America/New_York),
      stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; stop fixed at entry.
    2 generic: ADAPT, tick stop -> ATR multiple.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the quantity input stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_434593_ema_7_21_cross_atr_stop"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "fast": [7, 14],
    "sl_atr": [0.2, 1.5],
}
DEFAULT_PARAMS = {"fast": 7, "slow": 21, "atr_len": 14, "sl_atr": 0.2}


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


def _signals(bars_df, p):
    c = bars_df["close"]
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow"]), adjust=False).mean()
    le = ((f > s) & (f.shift(1) <= s.shift(1))).to_numpy()
    se = ((f < s) & (f.shift(1) >= s.shift(1))).to_numpy()
    return le, se


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    tr.iloc[0] = np.nan
    return tr.ewm(alpha=1 / n, adjust=False).mean()


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se = _signals(bars_df, p)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    frac = float(p["sl_atr"]) * _atr(bars_df, int(p["atr_len"])) / bars_df["close"]
    return {"sl_stop": frac.shift(1)}


def portfolio_kwargs(**params):
    return {}
