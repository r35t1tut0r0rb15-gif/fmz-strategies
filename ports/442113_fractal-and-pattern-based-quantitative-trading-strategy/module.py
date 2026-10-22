"""Two-bar breakouts with a fractal or candle pattern, broker days: the close crossing over the previous 2-bar high on a 3-bar high, bullish engulfing or hammer goes long, the mirror short; the close
crossing back under the previous 2-bar low closes a long (over the 2-bar high a short); reversing.
Port of FMZ strategy #442113 "Fractal and Pattern Based Quantitative Trading Strategy" (Fractal & Pattern Entry/Exit Strategy).

FMZ source id: 442113

Source
    https://www.fmz.com/strategy/442113 (PineScript v4, FMZ last modified 2024-02-19 14:32:45).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 122-162), fractal 3 bars; engulfing / hammer / hanging-man rules; 2-bar channel
    long = crossover(close, highest(2)[1]) and (high == highest(3) or bullish engulfing or hammer) -> entry Long;  short = crossunder(close, lowest(2)[1]) and (low == lowest(3) or bearish engulfing or hanging man) -> entry Short
    crossunder(close, lowest(2)[1]) -> close Long;  crossover(close, highest(2)[1]) -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * A close acts only on the held position; the close written after a reversing entry leaves the
      reversal standing (as #438020). strategy.entry reverses: REVERSAL INTENDED. No sizing code. Daily
      bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, channel crossings and candle patterns.
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

NAME = "fmz_442113_two_bar_breakout_fractal_pattern_reversal"
FAMILY = "candle_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "channel": [2, 3],
    "fractal": [3, 5],
}
DEFAULT_PARAMS = {"channel": 2, "fractal": 3}


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
    o, h, lo, c = bars_df["open"], bars_df["high"], bars_df["low"], bars_df["close"]
    f = int(p["fractal"])
    fh, fl = h == h.rolling(f).max(), lo == lo.rolling(f).min()
    o1, c1 = o.shift(1), c.shift(1)
    mx, mn = pd.concat([o, c], axis=1).max(axis=1), pd.concat([o, c], axis=1).min(axis=1)
    rng = h - lo
    bull_e = (o < c1) & (c > o1) & (c > o + (o1 - c1) * 2) & (lo < mn) & (h > mx) & (o1 > c1)
    bear_e = (o > c1) & (c < o1) & (o > c + (c1 - o1) * 2) & (h > mx) & (lo < mn) & (o1 < c1)
    hammer = (o < c) & (c > (h + lo + o * 2) / 4) & (c - o > rng * 0.6) & (h - c < rng * 0.1) & (o - lo < rng * 0.1)
    hang = (o > c) & (o < (h + lo + c * 2) / 4) & (o - c > rng * 0.6) & (h - o < rng * 0.1) & (c - lo < rng * 0.1)
    k = int(p["channel"])
    hk, lk = h.rolling(k).max().shift(1), lo.rolling(k).min().shift(1)
    xo = (c > hk) & (c1 <= hk.shift(1))
    xu = (c < lk) & (c1 >= lk.shift(1))
    el = (xo & (fh | bull_e | hammer)).to_numpy()
    es = (xu & (fl | bear_e | hang)).to_numpy()
    xl, xs = xu.to_numpy(), xo.to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    held = 0
    for i in range(m):
        new = held
        if el[i] and new != 1:
            new = 1
        if es[i] and new != -1:
            new = -1
        if xl[i] and held == 1 and new == 1:
            new = 0
        if xs[i] and held == -1 and new == -1:
            new = 0
        tgt[i] = new
        held = new
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    le = pd.Series((tgt == 1) & (prev != 1), index=ix)
    lx = pd.Series((prev == 1) & (tgt == 0), index=ix)
    se = pd.Series((tgt == -1) & (prev != -1), index=ix)
    sx = pd.Series((prev == -1) & (tgt == 0), index=ix)
    return le, lx, se, sx


def portfolio_kwargs(**params):
    return {}
