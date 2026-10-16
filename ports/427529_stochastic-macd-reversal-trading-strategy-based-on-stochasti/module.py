"""Combo: 123 reversal and MACD crossover with stops, broker days: long while both the 123-reversal
state (stochastic 100 / 1 / 2, level 1) and the MACD state (10 / 19, SMA signal 24) are long, short
while both are short, flat otherwise; a 10 % stop on the entry price, which steps up to +5 % once the
trade has been 10 % in profit (pending: see Marks).
Port of FMZ strategy #427529 "Reversal Trading Strategy Based on Stochastic and MACD Indicators".

FMZ source id: 427529

Source
    https://www.fmz.com/strategy/427529 (PineScript v4, FMZ last modified 2023-09-21 21:39:34).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 226-366), 123: 100 / 1 / 2 / 1; MACD 10 / 19 / 24; stops 10 / 10 / 5 %
    p123 as in the 123-reversal combos; pMACD = sma(macd, 24) < macd ? 1 : > ? -1 : pMACD[1]
    both 1 -> entry long; both -1 -> entry short; disagreement (0) -> close_all
    long stop = max(avg x (1 - 10 %), high > avg x 1.10 ? avg x 1.05 : 0, stop[1]) (short mirrors)

Interpretation choices (Pine rules in SURVEY_README.md; skill section 7)
    * The fixed part of the stop (10 % of the entry fill) is ported as sl_stop 0.10 (stops()).
    * The step to +5 % after a 10 % move is a ratchet the house trail cannot express (its lock-in
      moves the stop to the entry price, not to +5 %): rule 2, mark trailing_stop_pending, described
      in PORT_NOTES and not emitted. longStopPrice2 / 3 and lastStop* are never used by an order.
    * The leveraged quantity is sizing; the 2015-2999 window is the author's: dropped.
    * Daily bars are broker days; stops on daily bars: mark coarse_bar_stop.
    * Stop module: portfolio_kwargs {} (driver D4); REVERSAL INTENDED.
    * FREQ = "1D" from the backtest header (period 1d).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the fixed stop at entry, the step pending.
    2 generic: PASS, oscillator states and stops as fractions of price.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: leverage / equity quantity stored; stops quoted in original_sizing.txt.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_427529_combo_123_macd_stop"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "length": [100, 50],
    "level": [1, 50],
    "sl_pct": [10.0, 5.0],
}
DEFAULT_PARAMS = {"length": 100, "k_smoothing": 1, "d_length": 2, "level": 1, "fast": 10, "slow": 19,
                  "signal": 24, "sl_pct": 10.0}


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


def _state(up, dn):
    out = np.zeros(len(up), dtype=np.int8)
    s = 0
    for i in range(len(up)):
        if up[i]:
            s = 1
        elif dn[i]:
            s = -1
        out[i] = s
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    st = 100 * (c - lo.rolling(n).min()) / (h.rolling(n).max() - lo.rolling(n).min())
    fast = st.rolling(int(p["k_smoothing"])).mean()
    slow = fast.rolling(int(p["d_length"])).mean()
    c1, c2 = c.shift(1), c.shift(2)
    lvl = p["level"]
    s123 = _state(((c2 < c1) & (c > c1) & (fast < slow) & (fast > lvl)).to_numpy(),
                  ((c2 > c1) & (c < c1) & (fast > slow) & (fast < lvl)).to_numpy())
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    sig = macd.rolling(int(p["signal"])).mean()
    smacd = _state((sig < macd).to_numpy(), (sig > macd).to_numpy())
    combo = np.where((s123 == 1) & (smacd == 1), 1, np.where((s123 == -1) & (smacd == -1), -1, 0))
    idx = bars_df.index
    # entries on every bar of the state (Pine re-enters after a stop-out); flat state closes
    le = pd.Series(combo == 1, index=idx)
    se = pd.Series(combo == -1, index=idx)
    flat = pd.Series(combo == 0, index=idx)
    return le, flat.copy(), se, flat.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_pct"]) / 100}


def portfolio_kwargs(**params):
    return {}
