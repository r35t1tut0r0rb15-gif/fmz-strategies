"""EMA 9 / 21 crossings on the EMA 50 side with RSI 14 inside 40-70 / 30-60, broker days: the up-cross goes long and the down-cross goes short, each with a 0.5 % stop and a 1 % target from the signal close; reversing.
Port of FMZ strategy #483120 "多重均线交叉与RSI动量联动短线自适应交易策略-Multi-EMA-Crossover-with-RSI-Momentum-Adaptive-Scalping-Strategy" (RSI + EMA Scalping Strategy).

FMZ source id: 483120

Source
    https://www.fmz.com/strategy/483120 (PineScript v5, FMZ last modified 2025-02-21 14:27:45).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 93-129), EMA 9 / 21 / 50; RSI 14; stop 0.5 %; target 1 %
    crossover(ema9, ema21) and close > ema50 and 40 < rsi < 70 -> entry Buy + exit(stop = close x 0.995, limit = close x 1.01)
    crossunder(ema9, ema21) and close < ema50 and 30 < rsi < 60 -> entry Sell + exit(stop = close x 1.005, limit = close x 0.99)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The levels are fixed at the signal close and sent as fractions of the fill open (a level at or
      through it is marketable and closed one bar late, as #458256). The crossings alternate, so a side
      never re-sends its bracket while held. An entry on the other side reverses (REVERSAL INTENDED). Stop
      module: portfolio_kwargs {} (driver D4). Stops on daily bars: mark coarse_bar_stop. No sizing code.
      Daily bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; percent bracket as fractions of the fill.
    2 generic: PASS, EMA crossings with an EMA side and RSI bands.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_483120_ema9_21_cross_ema50_side_rsi_band_pct_bracket_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "stop_loss_percent": [0.5, 1.0],
    "target_percent": [1.0, 2.0],
}
DEFAULT_PARAMS = {"stop_loss_percent": 0.5, "target_percent": 1.0}


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


def _rsi(c, n):
    d = c.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    r = 100 - 100 / (1 + up / dn)
    r = r.where(dn != 0, 100.0).where(up != 0, 0.0)
    return r.where(up.notna() & dn.notna())


def _signals(bars_df, p):
    c = bars_df["close"]

    def ema(x, n):
        return x.ewm(span=n, adjust=False).mean()

    e9, e21, e50 = ema(c, 9), ema(c, 21), ema(c, 50)
    r = _rsi(c, 14)
    le = (e9 > e21) & (e9.shift(1) <= e21.shift(1)) & (c > e50) & (r > 40) & (r < 70)
    se = (e9 < e21) & (e9.shift(1) >= e21.shift(1)) & (c < e50) & (r < 60) & (r > 30)
    a, b = float(p["stop_loss_percent"]) / 100, float(p["target_percent"]) / 100
    lvl = {"l_sl": c * (1 - a), "l_tp": c * (1 + b), "s_sl": c * (1 + a), "s_tp": c * (1 - b)}
    return le, se, lvl


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf, sf = le.shift(1, fill_value=False), se.shift(1, fill_value=False)
    l_thr = (lvl["l_sl"].shift(1) >= o) | (lvl["l_tp"].shift(1) <= o)    # marketable at the fill
    s_thr = (lvl["s_sl"].shift(1) <= o) | (lvl["s_tp"].shift(1) >= o)
    return le, lf & l_thr & ~le & ~se, se, sf & s_thr & ~se & ~le


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    l_sl, l_tp = 1 - lvl["l_sl"].shift(1) / o, lvl["l_tp"].shift(1) / o - 1
    s_sl, s_tp = lvl["s_sl"].shift(1) / o - 1, 1 - lvl["s_tp"].shift(1) / o
    sl = l_sl.where(lf, s_sl)
    tp = l_tp.where(lf, s_tp)
    return {"sl_stop": sl.where(sl > 0), "tp_stop": tp.where(tp > 0)}


def portfolio_kwargs(**params):
    return {}
