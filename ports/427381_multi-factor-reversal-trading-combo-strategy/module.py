"""Combo: 123 reversal and FSK (fast and slow kurtosis), broker days: long while both the 123-reversal
state (stochastic 15 / 1 / 3, level 50) and the FSK state (EMA 65 of the momentum of 3-bar momentum
and its WMA 3 both above 0) are long, short while both are short, flat otherwise.
Port of FMZ strategy #427381 "Multi-factor Reversal Trading Combo Strategy".

FMZ source id: 427381

Source
    https://www.fmz.com/strategy/427381 (PineScript v4, FMZ last modified 2023-09-20 15:13:58).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 178-213), 123: 15 / 1 / 3 / 50; FSK trigger 0
    r = mom(mom(close, 3), 1); a = ema(r, 65); w = wma(a, 3); pFSK = a > 0 and w > 0 ? 1 : -1
    p123 as in the 123-reversal combos; both 1 -> long; both -1 -> short; otherwise close_all

Interpretation choices (Pine rules in SURVEY_README.md; as worker A's 123-reversal combos)
    * The FSK momentum is a price difference compared with 0: its sign only (scale-free).
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
    * REVERSAL INTENDED; disagreement closes. "Trade reverse" is off.
    * FREQ = "1D" from the backtest header (period 1d).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, oscillator states and signs.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427381_combo_123_fsk"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [15, 9],
    "level": [50, 40],
    "fsk_ema": [65, 30],
}
DEFAULT_PARAMS = {"length": 15, "k_smoothing": 1, "d_length": 3, "level": 50, "fsk_ema": 65, "trigger": 0.0}


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


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


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
    r = (c - c.shift(3)).diff()
    a = r.ewm(span=int(p["fsk_ema"]), adjust=False).mean()
    w = np.arange(1, 4, dtype=float)
    wa = a.rolling(3).apply(lambda x: np.dot(x, w) / w.sum(), raw=True)
    t = p["trigger"]
    sfsk = np.where((a > t) & (wa > t), 1, -1).astype(np.int8)
    tgt = np.where((s123 == 1) & (sfsk == 1), 1, np.where((s123 == -1) & (sfsk == -1), -1, 0)).astype(np.int8)
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
