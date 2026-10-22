"""Close crossings of the EMA 20 on the side of the EMA 50, daily bars: the cross up over the EMA 50 goes long with a 1 ATR stop and 1.5 ATR target from the signal close, the cross down under it goes short with the mirror; reversing.
Port of FMZ strategy #475637 "多重均线协同趋势波动交易策略基于ATR动态风控-Multi-EMA-Trend-Following-Swing-Trading-Strategy-with-ATR-Based-Risk-Management" (EMA Swing Strategy with ATR).

FMZ source id: 475637

Source
    https://www.fmz.com/strategy/475637 (PineScript v6, FMZ last modified 2024-12-20 17:06:20).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 98-148), EMA 20 / 50 / 100 (100 plotted); ATR 14; risk-reward 1.5; 5 contracts
    crossover(close, ema20) and close > ema50 -> sl := close - atr, tp := close + 1.5 atr, entry Long + exit;  crossunder and close < ema50 -> mirror for Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is sent once, on the signal bar, from its close and ATR: sent as fractions of the fill
      open; a level at or through it is marketable and closed one bar late (as #458256). Close
      crossings of the EMA 20 alternate, so no repeat signal re-sends it. REVERSAL INTENDED. Stop module:
      portfolio_kwargs {} (driver D4). Stops on daily bars: mark coarse_bar_stop. The contract count is
      not ported. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; signal-bar ATR bracket as fractions of the fill.
    2 generic: PASS, EMA crossings with an ATR bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: contract count stored, not ported.
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

NAME = "fmz_475637_close_cross_ema20_ema50_side_atr_bracket_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "rr": [1.5, 3.0],
    "ema_mid": [50, 100],
}
DEFAULT_PARAMS = {"rr": 1.5, "ema_mid": 50, "ema_short": 20}


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
    c = bars_df["close"]
    e20 = c.ewm(span=int(p["ema_short"]), adjust=False).mean()
    e50 = c.ewm(span=int(p["ema_mid"]), adjust=False).mean()
    le = (c > e20) & (c.shift(1) <= e20.shift(1)) & (c > e50)
    se = (c < e20) & (c.shift(1) >= e20.shift(1)) & (c < e50)
    atr = _atr(bars_df, 14)
    rr = float(p["rr"])
    lvl = {"l_sl": c - atr, "l_tp": c + rr * atr, "s_sl": c + atr, "s_tp": c - rr * atr}
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
