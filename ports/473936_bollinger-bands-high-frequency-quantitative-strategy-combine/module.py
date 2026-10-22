"""Previous-bar breaks after a bar outside the Bollinger 20 / 2 bands, 2-day bars: a high crossing over the previous high, when the previous high was under the lower band, goes long with the previous low as stop and a 1:1 target; the mirror goes short; reversing.
Port of FMZ strategy #473936 "Bollinger Bands High Frequency Quantitative Strategy Combined with High Low Breakout System" (Bollinger Band Scalping).

FMZ source id: 473936

Source
    https://www.fmz.com/strategy/473936 (PineScript v5, FMZ last modified 2024-12-04 15:15:50).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 88-150), BB 20, 2 sd; stop = previous low / high, target 1 : 1 from the previous high / low
    crossover(high, high[1]) and high[1] < lowerBB[1] -> entry Buy, exit(limit = high[1] + (high[1] - low[1]), stop = low[1]);  crossunder(low, low[1]) and low[1] > upperBB[1] -> entry Sell, exit(limit = low[1] - (high[1] - low[1]), stop = high[1])

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is sent once, on the signal bar, from the bar before it: sent as fractions of the
      fill open; a level at or through it is marketable and closed one bar late (as #458256). REVERSAL
      INTENDED. Stop module: portfolio_kwargs {} (driver D4). Stops on 2-day bars: mark
      coarse_bar_stop. No sizing code. FREQ = "2D" from the backtest header (blocks of 2 broker days,
      as #429148).

Admission criteria
    1 fits the interface: PASS, bar-close orders; signal-bar bracket as fractions of the fill.
    2 generic: PASS, band-outside bar breaks with a 1 : 1 bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_473936_bb20_outside_bar_break_prev_range_bracket_reversal"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2D"  # backtest header period: 2d (blocks of 2 broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "length": [20, 50],
    "mult": [2.0, 1.5],
}
DEFAULT_PARAMS = {"length": 20, "mult": 2.0, "days": 2}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _multiday(raw_1m_df, days):
    """Blocks of `days` broker days counted from 1970-01-01, each stamped with its first minute."""
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    key = np.asarray((broker_day(df.index) - pd.Timestamp("1970-01-01")).days // days)
    bars = df.groupby(key).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(key).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    p = {**DEFAULT_PARAMS, **params}
    return _multiday(raw_1m_df, int(p["days"]))


def _signals(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    basis = c.rolling(n).mean()
    dev = float(p["mult"]) * c.rolling(n).std(ddof=0)
    up, dn = basis + dev, basis - dev
    h1, l1 = h.shift(1), lo.shift(1)
    le = (h > h1) & (h1 <= h.shift(2)) & (h1 < dn.shift(1))
    se = (lo < l1) & (l1 >= lo.shift(2)) & (l1 > up.shift(1))
    rng = h1 - l1
    lvl = {"l_sl": l1, "l_tp": h1 + rng, "s_sl": h1, "s_tp": l1 - rng}
    return le, se, lvl


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    sf = se.shift(1, fill_value=False)
    l_thr = (lvl["l_sl"].shift(1) >= o) | (lvl["l_tp"].shift(1) <= o)    # marketable at the fill
    s_thr = (lvl["s_sl"].shift(1) <= o) | (lvl["s_tp"].shift(1) >= o)
    return le, lf & l_thr & ~se, se, sf & s_thr & ~le


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    sl_f = (1 - lvl["l_sl"].shift(1) / o).where(lf, lvl["s_sl"].shift(1) / o - 1)
    tp_f = (lvl["l_tp"].shift(1) / o - 1).where(lf, 1 - lvl["s_tp"].shift(1) / o)
    return {"sl_stop": sl_f.where(sl_f > 0), "tp_stop": tp_f.where(tp_f > 0)}


def portfolio_kwargs(**params):
    return {}
