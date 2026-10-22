"""MACD (12 / 26 / 9) histogram colour turns, broker days: a falling negative histogram turning up goes long with a stop 3 ATR under the low and a target 10 ATR over the close; a falling positive histogram turning up goes short with a stop 3 ATR over the high and a target 10 ATR under the close; reversing.
Port of FMZ strategy #477956 "Enhanced Price Volume Trend Momentum Strategy" (軒割MACD 空心量能不足策略).

FMZ source id: 477956

Source
    https://www.fmz.com/strategy/477956 (PineScript v5, FMZ last modified 2025-01-10 15:40:37).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 83-167), MACD 12 / 26 / 9 (EMA); ATR 14; TP 10 x ATR, SL 3 x ATR; qty 1; long and short on
    darkRed[1] and lightRed (hist < 0, now rising) -> entry Long (qty 1) + exit(stop = low - 3 atr, limit = close + 10 atr);  darkGreen[1] and lightGreen (hist >= 0, now rising) -> entry Short + exit(stop = high + 3 atr, limit = close - 10 atr)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The short signal is a positive histogram that starts rising again, as written. The bracket is sent
      on each signal bar: the opening signal's levels are ported, sent as fractions of the fill open (a
      level at or through it is marketable and closed one bar late, as #458256); the colour turns can
      repeat inside a trade and re-send it, which is not followed (as #434428, mark
      trailing_stop_pending). REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). Stops on
      daily bars: mark coarse_bar_stop. The fixed qty 1 is sizing. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; signal-bar ATR bracket as fractions of the fill.
    2 generic: PASS, MACD histogram colour turns with an ATR bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: qty 1 stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_477956_macd_hist_colour_turn_atr_bracket_reversal"
FAMILY = "macd"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "tp_atr": [10, 3],
    "sl_atr": [3, 1],
}
DEFAULT_PARAMS = {"tp_atr": 10, "sl_atr": 3, "atr_period": 14}


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


def _rma(x, n):
    """Wilder smoothing as Pine's rma: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def _signals(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    hist = macd - macd.ewm(span=9, adjust=False).mean()
    hp = hist.shift(1)
    dark_g, light_g = (hist >= 0) & (hist <= hp), (hist >= 0) & (hist > hp)
    dark_r, light_r = (hist < 0) & (hist <= hp), (hist < 0) & (hist > hp)
    le = dark_r.shift(1, fill_value=False) & light_r
    se = dark_g.shift(1, fill_value=False) & light_g
    atr = _atr(bars_df, p["atr_period"])
    ts, ss = float(p["tp_atr"]), float(p["sl_atr"])
    lvl = {"l_sl": lo - ss * atr, "l_tp": c + ts * atr, "s_sl": h + ss * atr, "s_tp": c - ts * atr}
    return le, se, lvl


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    sf = se.shift(1, fill_value=False)
    l_thr = (lvl["l_sl"].shift(1) >= o) | (lvl["l_tp"].shift(1) <= o)    # marketable at the fill
    s_thr = (lvl["s_sl"].shift(1) <= o) | (lvl["s_tp"].shift(1) >= o)
    return le, lf & l_thr & ~se & ~le, se, sf & s_thr & ~le & ~se


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
