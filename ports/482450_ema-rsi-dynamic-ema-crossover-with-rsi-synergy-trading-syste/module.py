"""EMA 9 / 21 crossings with RSI 14 on the 50 side, broker days: the cross up with RSI over 50 goes long, the cross down under 50 goes short, each with a 25-point stop and a 125-point target from the signal close; reversing.
Port of FMZ strategy #482450 "动态EMA交叉与RSI协同交易系统-Dynamic-EMA-Crossover-with-RSI-Synergy-Trading-System" (Lukhi EMA Crossover_TWL Strategy).

FMZ source id: 482450

Source
    https://www.fmz.com/strategy/482450 (PineScript v6, FMZ last modified 2025-02-18 14:57:55).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 92-166), EMA 9 / 21; RSI 14; stop 25 points; target = 5000 / (1000 / 25) = 125 points; lot 1; capital 15000
    crossover(ema9, ema21) and rsi > 50 -> entry Buy (lot 1) + exit(stop = close - 25, limit = close + 125);  crossunder and rsi < 50 -> entry Sell + exit(stop = close + 25, limit = close - 125)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The same rules as #481347 with a 25-point stop: the target reduces to a fixed 125 points (5000 /
      (1000 / 25)); both are price amounts, ported as fractions of 42000 of the signal close (5.95e-04 /
      2.98e-03), sent as fractions of the fill open (a level at or through it is marketable and closed
      one bar late, as #458256); the crossings alternate, so no repeat re-sends them. REVERSAL INTENDED.
      Stop module: portfolio_kwargs {} (driver D4). Stops on daily bars: mark coarse_bar_stop. The lot and
      capital are sizing. Daily bars are broker days (17:00 America/New_York), stamped with their first
      minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; point bracket as fractions of the fill.
    2 generic: PASS, EMA crossings with an RSI filter and a point bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: lot 1, capital 15000, risk 1000 / target 5000 stored; the bracket reduces to fixed points.
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

NAME = "fmz_482450_ema9_21_cross_rsi50_point25_bracket_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_frac": [5.95238e-04, 0.01],
    "tp_frac": [2.97619e-03, 0.05],
}
DEFAULT_PARAMS = {"sl_frac": 5.95238e-04, "tp_frac": 2.97619e-03, "fast": 9, "slow": 21, "rsi_length": 14}


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
    return 100 - 100 / (1 + up / dn)


def _signals(bars_df, p):
    c = bars_df["close"]
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow"]), adjust=False).mean()
    r = _rsi(c, int(p["rsi_length"]))
    le = (f > s) & (f.shift(1) <= s.shift(1)) & (r > 50)
    se = (f < s) & (f.shift(1) >= s.shift(1)) & (r < 50)
    sl, tp = float(p["sl_frac"]) * c, float(p["tp_frac"]) * c
    lvl = {"l_sl": c - sl, "l_tp": c + tp, "s_sl": c + sl, "s_tp": c - tp}
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
