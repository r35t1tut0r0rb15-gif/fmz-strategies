"""EMA 9 / 21 crossings with RSI 14 short of the extreme, broker days: the cross up with RSI under 70 goes long, the cross down with RSI over 30 goes short, each with a 1.5 ATR stop and 2 ATR target from the signal close; reversing.
Port of FMZ strategy #481349 "跨周期动量均线交叉策略结合RSI与ATR动态止损-Cross-Period-Momentum-EMA-Strategy-with-RSI-and-Dynamic-ATR-Stop-Loss" (Day Trading EMA/RSI Strategy).

FMZ source id: 481349

Source
    https://www.fmz.com/strategy/481349 (PineScript v5, FMZ last modified 2025-02-10 14:34:58).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 125-180), EMA 9 / 21; RSI 14, 70 / 30; ATR 14 x 1.5 stop, x 2 target; 200 % of equity
    crossover(ema9, ema21) and rsi < 70 -> entry Long + exit(stop = close - 1.5 atr, limit = close + 2 atr);  crossunder and rsi > 30 -> entry Short + exit(mirror)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is sent once, on the signal bar, from its close and ATR: sent as fractions of the fill
      open (a level at or through it is marketable and closed one bar late, as #458256); the crossings
      alternate, so no repeat re-sends it. REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4).
      Stops on daily bars: mark coarse_bar_stop. The 200 % of equity size is sizing. Daily bars are broker
      days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; signal-bar ATR bracket as fractions of the fill.
    2 generic: PASS, EMA crossings with an RSI filter and an ATR bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 200 % of equity stored, not ported.
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

NAME = "fmz_481349_ema9_21_cross_rsi_filter_atr_bracket_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "atr_mult": [1.5, 2.5],
    "tp_factor": [2.0, 4.0],
}
DEFAULT_PARAMS = {"atr_mult": 1.5, "tp_factor": 2.0, "fast": 9, "slow": 21, "rsi_period": 14, "atr_period": 14}


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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def _signals(bars_df, p):
    c = bars_df["close"]
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow"]), adjust=False).mean()
    r = _rsi(c, int(p["rsi_period"]))
    le = (f > s) & (f.shift(1) <= s.shift(1)) & (r < 70)
    se = (f < s) & (f.shift(1) >= s.shift(1)) & (r > 30)
    atr = _atr(bars_df, p["atr_period"])
    sl, tp = float(p["atr_mult"]) * atr, float(p["tp_factor"]) * atr
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
