"""Heikin Ashi / Kaufman (Gustavo), broker days: the Heikin Ashi hlc3 crossing above an EMA 20 of a one-step Kaufman blend
of the Heikin Ashi hlc3 goes long, crossing below goes short.
Port of FMZ strategy #430753 "Momentum Capture Strategy Based on Moving Average" (Heikin Ashi EMA v5 no repaint).

FMZ source id: 430753

Source
    https://www.fmz.com/strategy/430753 (PineScript v5, FMZ last modified 2023-11-01 15:55:51).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 194-237), HA timeframe D (the chart), EMA 20, Kaufman length 5, fast 2.5, slow 20
    on the Heikin Ashi ticker: x = hlc3; eff = |x - x[5]| / sum(|x - x[1]|, 5); sc = (eff (2/3.5 - 2/21) + 2/21)^2
    kama1 = x[1] + sc (x - x[1])          (nAMA is hlc3, not recursive, as written)
    fma = ema(HA hlc3, 1); sma = ema(kama1, 20)
    crossover(fma, sma) -> entry long;  crossunder -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The Heikin Ashi candles are built from the chart's bars (HA close = ohlc4, HA open = mean of the
      previous HA open and close, HA high / low include them); "D" on the 1-day header chart is the
      chart itself, so both securities read the current completed HA bar (no higher timeframe).
    * nAMA is the plain hlc3, so the Kaufman line is one step from the previous hlc3, as written.
      The shift input is 0.
    * strategy.entry reverses: REVERSAL INTENDED. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Heikin Ashi values and moving averages.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the commented-out order size stored in original_sizing.txt.
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

NAME = "fmz_430753_heikin_kaufman_cross"
FAMILY = "heikin_ashi_trend"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "sloma": [20, 50],
    "length": [5, 10],
}
DEFAULT_PARAMS = {"sloma": 20, "length": 5, "fastend": 2.5, "slowend": 20}


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


def _heikin_ashi(bars):
    o, h, lo, c = (bars[k].to_numpy(dtype=float) for k in ("open", "high", "low", "close"))
    hc = (o + h + lo + c) / 4
    ho = np.empty(len(c))
    for i in range(len(c)):
        ho[i] = (o[i] + c[i]) / 2 if i == 0 else (ho[i - 1] + hc[i - 1]) / 2
    hh = np.maximum(h, np.maximum(ho, hc))
    hl = np.minimum(lo, np.minimum(ho, hc))
    return pd.DataFrame({"high": hh, "low": hl, "close": hc}, index=bars.index)


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    ha = _heikin_ashi(bars_df)
    x = (ha["high"] + ha["low"] + ha["close"]) / 3
    n = int(p["length"])
    noise = x.diff().abs().rolling(n).sum()
    eff = ((x - x.shift(n)).abs() / noise.replace(0.0, np.nan)).fillna(0.0)
    fe, se_ = 2 / (float(p["fastend"]) + 1), 2 / (float(p["slowend"]) + 1)
    sc = (eff * (fe - se_) + se_) ** 2
    x1 = x.shift(1).fillna(0.0)
    kama1 = x1 + sc * (x - x1)
    slow = kama1.ewm(span=int(p["sloma"]), adjust=False).mean()
    xo = ((x > slow) & (x.shift(1) <= slow.shift(1))).to_numpy()
    xu = ((x < slow) & (x.shift(1) >= slow.shift(1))).to_numpy()
    m = len(x)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if xo[i]:
            pos = 1
        elif xu[i]:
            pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
