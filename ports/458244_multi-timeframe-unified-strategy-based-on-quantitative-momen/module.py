"""Broker days, long only: the EMA 5 crossing over the EMA 15 (or the SMA 20 over the SMA 50) while the squeeze state is on or off (not "no squeeze") and the squeeze momentum is positive goes long; that trade closes only on its own pair's opposite crossing while in a squeeze state with negative momentum.
Port of FMZ strategy #458244 "Multi Timeframe Unified Strategy Based on Quantitative Momentum and Convergence Divergence" (Combined Scalping and Swing Trading Strategy with Squeeze Momentum).

FMZ source id: 458244

Source
    https://www.fmz.com/strategy/458244 (PineScript v5, FMZ last modified 2024-07-31 11:33:59).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 225-317), EMA 5 / 15 (scalp), SMA 20 / 50 (swing); BB 20 x 2, KC 20 x 1.5 (true range); linreg 20 momentum
    scalpBuySignal and not noSqz and val > 0 -> entry "Scalp Buy";  scalpSellSignal and not noSqz and val < 0 -> close "Scalp Buy"
    swingBuySignal and not noSqz and val > 0 -> entry "Swing Buy";  swingSellSignal and not noSqz and val < 0 -> close "Swing Buy"

Interpretation choices (Pine rules in SURVEY_README.md)
    * Default pyramiding: one long at a time, opened by whichever entry id fires first (the scalp one when
      both fire on one bar, its call comes first); only that id's close ends it, the other id's close
      does nothing. A buy needs val > 0 and a close needs val < 0, so they never meet on one bar.
      sqzOff (BB outside KC) counts as a squeeze state, as written. ta.tr(true) is high - low on the
      first bar; ta.stdev is the population deviation. Volume only plots (held for volume, not used).
      Long only. No sizing code. Daily bars are broker days (17:00 America/New_York), stamped with their
      first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MA crossings filtered by the squeeze state and momentum.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd
from numpy.lib.stride_tricks import sliding_window_view

NAME = "fmz_458244_scalp_swing_ma_cross_squeeze_momentum_long_only"
FAMILY = "squeeze_momentum"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "bb_mult": [2.0, 2.5],
    "kc_mult": [1.5, 2.0],
}
DEFAULT_PARAMS = {"bb_len": 20, "bb_mult": 2.0, "kc_len": 20, "kc_mult": 1.5}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close", "volume"]].dropna(subset=["close"])
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def _linreg(c, n):
    """ta.linreg(c, n, 0): the n-bar least-squares line's value at the newest bar."""
    v = c.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    if len(v) >= n:
        x = np.arange(n, dtype=float)
        xm = x.mean()
        w = 1.0 / n + (x - xm) * (n - 1 - xm) / ((x - xm) ** 2).sum()
        out[n - 1:] = sliding_window_view(v, n) @ w
    return pd.Series(out, index=c.index)


def _cross(a, b):
    return (a > b) & (a.shift(1) <= b.shift(1))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    e5, e15 = c.ewm(span=5, adjust=False).mean(), c.ewm(span=15, adjust=False).mean()
    s20, s50 = c.rolling(20).mean(), c.rolling(50).mean()
    nb, nk = int(p["bb_len"]), int(p["kc_len"])
    basis, dev = c.rolling(nb).mean(), float(p["bb_mult"]) * c.rolling(nb).std(ddof=0)
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    ma, rng = c.rolling(nk).mean(), tr.rolling(nk).mean() * float(p["kc_mult"])
    up_bb, lo_bb, up_kc, lo_kc = basis + dev, basis - dev, ma + rng, ma - rng
    sqz_on = (lo_bb > lo_kc) & (up_bb < up_kc)
    sqz_off = (lo_bb < lo_kc) & (up_bb > up_kc)
    sq = sqz_on | sqz_off
    val = _linreg(c - (h.rolling(nk).max() + lo.rolling(nk).min()) / 2, nk)
    pos_v, neg_v = val > 0, val < 0
    sc_b = (_cross(e5, e15) & sq & pos_v).to_numpy()
    sc_s = (_cross(e15, e5) & sq & neg_v).to_numpy()
    sw_b = (_cross(s20, s50) & sq & pos_v).to_numpy()
    sw_s = (_cross(s50, s20) & sq & neg_v).to_numpy()
    m = len(sc_b)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    held = None                            # which entry id holds the long
    for i in range(m):
        if held is None:
            if sc_b[i]:
                held, le[i] = "scalp", True
            elif sw_b[i]:
                held, le[i] = "swing", True
        elif (held == "scalp" and sc_s[i]) or (held == "swing" and sw_s[i]):
            held, lx[i] = None, True
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
