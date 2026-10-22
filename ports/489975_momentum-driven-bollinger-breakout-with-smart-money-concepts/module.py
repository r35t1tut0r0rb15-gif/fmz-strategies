"""Close crossings out of the Bollinger 55 / 2 bands with a structure shift and a strong-bodied candle, broker days: the break up above the SMA 55 trend goes long, the break down below it goes short; a close back under (over) the basis, or 1 % beyond the 20-bar extreme, closes; reversing.
Port of FMZ strategy #489975 "Momentum Driven Bollinger Breakout with Smart Money Concepts Integration Strategy" (02 SMC + BB Breakout v4 + Momentum Color).

FMZ source id: 489975

Source
    https://www.fmz.com/strategy/489975 (PineScript v6, FMZ last modified 2025-04-10 16:12:38).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 183-270), BB 55 / 2; HTF "1D" (the chart); order-block 20; swing 12; momentum body 70 %; 5 % of equity sizing
    previous_high := valuewhen(high > highest(high[1], 12), high[1]);  previous_low mirror
    crossover(close, upper) and close > sma(close, 55) and close > previous_high and body >= 70 % up -> entry Long;  mirror -> entry Short
    crossunder(close, basis) or close < lowest(low, 20) x 0.99 -> close Long;  crossover(close, basis) or close > highest(high, 20) x 1.01 -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "1D" request on the daily chart is the chart itself. The structure levels are valuewhen values,
      followed in a loop. An entry on the other side reverses (REVERSAL INTENDED). The 5 % quantity is
      sizing. Daily bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ =
      "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Bollinger breakouts with structure-shift and momentum-candle filters.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: 5 % of equity sizing stored, not ported.
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

NAME = "fmz_489975_bb55_breakout_structure_shift_momentum_candle_reversal"
FAMILY = "bollinger_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [55, 20],
    "momentum_body_percent": [0.7, 0.5],
}
DEFAULT_PARAMS = {"length": 55, "momentum_body_percent": 0.7, "mult": 2.0, "ob_length": 20, "swing_length": 12}


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
    n = int(p["length"])
    basis = c.rolling(n).mean()
    sd = c.rolling(n).std(ddof=0)
    upper, lower = basis + float(p["mult"]) * sd, basis - float(p["mult"]) * sd
    trend = c > basis
    sw = int(p["swing_length"])
    brk_h = (h > h.shift(1).rolling(sw).max()).to_numpy()
    brk_l = (lo < lo.shift(1).rolling(sw).min()).to_numpy()
    h1, l1 = h.shift(1).to_numpy(), lo.shift(1).to_numpy()
    m = len(c)
    ph, pl = np.full(m, np.nan), np.full(m, np.nan)
    vh = vl = np.nan
    for i in range(m):
        if brk_h[i]:
            vh = h1[i]
        if brk_l[i]:
            vl = l1[i]
        ph[i], pl[i] = vh, vl
    rng = h - lo
    body_pct = ((c - o).abs() / rng.where(rng > 0)).where(rng > 0, 0.0)
    mb = float(p["momentum_body_percent"])
    lm, sm = (body_pct >= mb) & (c > o), (body_pct >= mb) & (c < o)
    le = (c > upper) & (c.shift(1) <= upper.shift(1)) & trend & (c.to_numpy() > ph) & lm
    se = (c < lower) & (c.shift(1) >= lower.shift(1)) & ~trend & (c.to_numpy() < pl) & sm
    ob = int(p["ob_length"])
    lx = ((c < basis) & (c.shift(1) >= basis.shift(1))) | (c < lo.rolling(ob).min() * 0.99)
    sx = ((c > basis) & (c.shift(1) <= basis.shift(1))) | (c > h.rolling(ob).max() * 1.01)
    return le, lx & ~le & ~se, se, sx & ~se & ~le


def portfolio_kwargs(**params):
    return {}
