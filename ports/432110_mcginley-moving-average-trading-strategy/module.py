"""McGinley dynamic pull-backs, broker days: with the EMA 21 at or above the EMA 42 and the close above the McGinley line
(20, k 0.6), a low crossing under the EMA 21 with the close back above it goes long; the mirror goes short. A 20-tick
target becomes an ATR fraction; the close below the McGinley line and both EMAs closes a long (mirror for shorts).
Port of FMZ strategy #432110 "McGinley Moving Average Trading Strategy" (McGinley Dynamic Indicator (Maguila)).

FMZ source id: 432110

Source
    https://www.fmz.com/strategy/432110 (PineScript v4, FMZ last modified 2023-11-14 15:48:46).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 157-218), EMA 21 / 42, McGinley 20 / k 0.6, target 20 ticks, qty 1
    mdi := na(mdi[1]) ? close : mdi[1] + (close - mdi[1]) / max(k * period * pow(close / mdi[1], 4), 1)
    ema21 >= ema42 and close > mdi and crossunder(low, ema21) and close > ema21 -> entry long, exit(profit = 20)
    close < mdi and close < ema21 and close < ema42 -> close long;  mirror (crossover(high, ema21)) for shorts

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: profit = 20 ticks (2 USD on BTC_USDT, mintick 0.1) becomes tp_atr x the Wilder ATR
      14 of the signal bar as a fraction of its close (about 0.002 ATR on daily BTC), shifted one bar
      inside stops() and re-based on the fill; the grid adds 1 ATR. No stop-loss in the source.
    * The date window (2019-05-28 to 2030-05-28) is the author's backtest range: dropped, with its
      close_all outside the range. crossunder(low, ema21) = low < ema21 and low[1] >= ema21[1].
    * strategy.entry reverses: REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4).
      Daily bars are broker days (17:00 America/New_York), stamped with their first minute; stops on
      daily bars: mark coarse_bar_stop. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; target fixed at entry.
    2 generic: ADAPT, tick target -> ATR fraction.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: qty 1 stored in original_sizing.txt.
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

NAME = "fmz_432110_mcginley_ema_pullback"
FAMILY = "ma_trend"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "tp_atr": [0.002, 1.0],
    "md_period": [20, 10],
}
DEFAULT_PARAMS = {"ma1": 21, "ma2": 42, "md_period": 20, "md_k": 0.6, "atr_len": 14, "tp_atr": 0.002}


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


def _mcginley(c, period, k):
    cv = c.to_numpy(dtype=float)
    out = np.full(len(cv), np.nan)
    prev = np.nan
    for i, x in enumerate(cv):
        if np.isnan(prev):
            prev = x
        else:
            prev = prev + (x - prev) / max(k * period * (x / prev) ** 4, 1.0)
        out[i] = prev
    return pd.Series(out, index=c.index)


def _signals(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    m1 = c.ewm(span=int(p["ma1"]), adjust=False).mean()
    m2 = c.ewm(span=int(p["ma2"]), adjust=False).mean()
    md = _mcginley(c, int(p["md_period"]), float(p["md_k"]))
    cu_low = (lo < m1) & (lo.shift(1) >= m1.shift(1))
    co_high = (h > m1) & (h.shift(1) <= m1.shift(1))
    le = ((m1 >= m2) & (c > md) & cu_low & (c > m1)).astype(bool)
    lx = ((c < md) & (c < m1) & (c < m2)).astype(bool)
    se = ((m2 >= m1) & (c < md) & co_high & (c < m1)).astype(bool)
    sx = ((c > md) & (c > m1) & (c > m2)).astype(bool)
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    af = tr.ewm(alpha=1 / int(p["atr_len"]), adjust=False).mean() / c
    return le, lx, se, sx, af


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx, se, sx, _ = _signals(bars_df, p)
    return le, lx, se, sx


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    af = _signals(bars_df, p)[4]
    return {"tp_stop": (af * float(p["tp_atr"])).shift(1)}


def portfolio_kwargs(**params):
    return {}
