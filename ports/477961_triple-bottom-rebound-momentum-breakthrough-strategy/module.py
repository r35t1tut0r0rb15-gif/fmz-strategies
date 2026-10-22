"""EMA 5 / 20 crossings, broker days: the cross up goes long with a stop 2 ATR 14 under the signal close and a target 2 ATR over it; the cross down goes short with a stop 2 ATR over the signal high and a target 2 ATR under the close; reversing.
Port of FMZ strategy #477961 "Triple Bottom Rebound Momentum Breakthrough Strategy" (反彈三次突破策略).

FMZ source id: 477961

Source
    https://www.fmz.com/strategy/477961 (PineScript v5, FMZ last modified 2025-01-10 15:49:30).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 97-217), EMA 5 / 20; ATR 14, factor 2, profit factor 2; "three bounce" low tracking; 2-hour spacing; commission 0.001425, slippage 1; capital 100000
    low1..3 reset to na while any is na, then low3 := close;  trend_down and close > low2 and close > low1 -> long_breakout (never: low1 / low2 stay na)
    crossover(ema5, ema20) or long_breakout -> entry 做多 + exit(stop = low3 - 2 atr, limit = close + 2 atr);  crossunder -> entry 做空 + exit(stop = high + 2 atr, limit = close - 2 atr)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The low tracker resets all three lows to na on every bar (one of them is always na) and then sets
      low3 to the close, so low1 / low2 stay na, the breakout never fires and the long stop is the
      signal close - 2 ATR, as written. The 2-hour spacing always passes on daily bars. The bracket is
      sent once, on the signal bar: sent as fractions of the fill open (a level at or through it is
      marketable and closed one bar late, as #458256); the crossings alternate, so no repeat re-sends it.
      REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). Stops on daily bars: mark
      coarse_bar_stop. The commission and slippage settings are costs and are not ported (house cost
      model); the capital is sizing. Daily bars are broker days (17:00 America/New_York), stamped with
      their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; signal-bar ATR bracket as fractions of the fill.
    2 generic: PASS, EMA crossings with an ATR bracket (the breakout branch never fires).
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: capital stored; costs not ported.
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

NAME = "fmz_477961_ema5_20_cross_atr2_bracket_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "atr_factor": [2.0, 1.0],
    "profit_factor": [2.0, 4.0],
}
DEFAULT_PARAMS = {"atr_factor": 2.0, "profit_factor": 2.0, "fast": 5, "slow": 20, "atr_period": 14}


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
    h, c = bars_df["high"], bars_df["close"]
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow"]), adjust=False).mean()
    le = (f > s) & (f.shift(1) <= s.shift(1))
    se = (f < s) & (f.shift(1) >= s.shift(1))
    atr = _atr(bars_df, p["atr_period"])
    af, pf = float(p["atr_factor"]), float(p["profit_factor"])
    lvl = {"l_sl": c - af * atr, "l_tp": c + pf * atr, "s_sl": h + af * atr, "s_tp": c - pf * atr}
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
