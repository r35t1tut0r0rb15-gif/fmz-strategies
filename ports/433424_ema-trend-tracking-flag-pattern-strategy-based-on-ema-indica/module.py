"""Elliott-wave oscillator of the opens, broker days: the EMA 5 minus the EMA 13 of the opens crossing above a small
threshold goes long, crossing back below it goes short, and a long is closed when the oscillator falls under a lower
level. The price-unit levels 1.618 / 0.218 become ATR fractions.
Port of FMZ strategy #433424 "基于EMA指标的旗形趋势追踪策略Trend-Tracking-Flag-Pattern-Strategy-Based-on-EMA-Indicators" (ROCKET_EWO).

FMZ source id: 433424

Source
    https://www.fmz.com/strategy/433424 (PineScript v5, FMZ last modified 2023-11-27 15:30:29).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 154-184), EMA 5 / 13 of open; levels 1.618 (entries) and 0.218 (long exit), price units
    s2 = ema(open, 5) - ema(open, 13)
    crossover(s2, 1.618) -> entry long;  crossunder(s2, 1.618) -> entry short;  s2 < 0.218 -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the levels are price units (1.618 USD on daily BTC, about 0.002 ATR, i.e. the zero
      line). They become th_atr x Wilder ATR 14 of the same bar, the exit level th_atr x 0.218 / 1.618.
    * Each bar: the long close acts on the position held at the start of the bar, then an entry wins
      (the short entry reverses a long, as strategy.entry does). REVERSAL INTENDED. Daily bars are
      broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: ADAPT, price-unit oscillator levels -> ATR fractions.
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

NAME = "fmz_433424_ewo_open_threshold"
FAMILY = "momentum_oscillator_turn"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "th_atr": [0.002, 0.2],
    "slow": [13, 34],
}
DEFAULT_PARAMS = {"fast": 5, "slow": 13, "th_atr": 0.002, "atr_len": 14}


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
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    s2 = o.ewm(span=int(p["fast"]), adjust=False).mean() - o.ewm(span=int(p["slow"]), adjust=False).mean()
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    atr = tr.ewm(alpha=1 / int(p["atr_len"]), adjust=False).mean()
    th = float(p["th_atr"]) * atr
    ex = th * 0.218 / 1.618
    le = ((s2 > th) & (s2.shift(1) <= th.shift(1))).to_numpy()
    se = ((s2 < th) & (s2.shift(1) >= th.shift(1))).to_numpy()
    lx = (s2 < ex).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if pos == 1 and lx[i]:
            pos = 0
        if le[i]:
            pos = 1
        elif se[i]:
            pos = -1
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), pd.Series((prev == 1) & (tgt == 0), index=ix),
            pd.Series((tgt == -1) & (prev != -1), index=ix), pd.Series((prev == -1) & (tgt == 0), index=ix))


def portfolio_kwargs(**params):
    return {}
