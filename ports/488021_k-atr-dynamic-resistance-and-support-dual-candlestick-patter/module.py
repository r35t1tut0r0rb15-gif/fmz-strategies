"""Engulfing candles against the 50-bar support / resistance, 3-day bars: a bullish engulfing above the 50-bar low goes long, a bearish engulfing below the 50-bar high goes short, each with a 1.5 ATR 14 stop and a 3 ATR target from the signal close; reversing.
Port of FMZ strategy #488021 "动态阻力与支撑的双K线形态ATR风险控制量化交易策略-Dynamic-Resistance-and-Support-Dual-Candlestick-Pattern-ATR-Risk-Management-Quantitative-Trading-Strategy" (Ai ProSR V.1).

FMZ source id: 488021

Source
    https://www.fmz.com/strategy/488021 (PineScript v5, FMZ last modified 2025-03-24 14:24:55).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 161-206), lookback 50; ATR 14 x 1.5; target 2 x the stop
    bullish engulfing and close > lowest(low, 50) -> entry Buy + exit(stop = close - 1.5 atr, limit = close + 3 atr)
    bearish engulfing and close < highest(high, 50) -> entry Sell + mirror

Interpretation choices (Pine rules in SURVEY_README.md)
    * The 50-bar levels include the signal bar, as written. The bracket is set on the signal bar from its
      close and sent as fractions of the fill open (a level at or through it is marketable and closed one
      bar late, as #458256). A later same-side pattern while held re-sends the bracket; the port keeps the
      opening levels, mark trailing_stop_pending (as #434428). An entry on the other side reverses
      (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (driver D4). Stops on bars longer than 1 hour:
      mark coarse_bar_stop. No sizing code. MPL 2.0 source (the notice is kept: Mozilla Public License 2.0,
      © watcharaphon0619). Bars are blocks of three broker days (17:00 America/New_York) counted from
      1970-01-01, stamped with their first minute. FREQ = "3D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; ATR bracket as fractions of the fill.
    2 generic: PASS, engulfing patterns with support / resistance filters and an ATR bracket.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: three-broker-day blocks (17:00 America/New_York, DST by the zone).
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_488021_engulfing_sr50_atr15_bracket_2r_reversal"
FAMILY = "candlestick_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "3D"  # backtest header period: 3d (three broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "atrMultiplier": [1.5, 2.5],
    "lookback": [50, 20],
}
DEFAULT_PARAMS = {"atrMultiplier": 1.5, "lookback": 50, "atrLength": 14, "days": 3}


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


def _signals(bars_df, p):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    n = int(p["lookback"])
    res, sup = h.rolling(n).max(), lo.rolling(n).min()
    o1, c1 = o.shift(1), c.shift(1)
    bull = (c1 < o1) & (c > o) & (c > o1) & (o < c1)
    bear = (c1 > o1) & (c < o) & (c < o1) & (o > c1)
    le = bull & (c > sup)
    se = bear & (c < res)
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]
    a = _rma(tr, int(p["atrLength"])) * float(p["atrMultiplier"])
    lvl = {"l_sl": c - a, "l_tp": c + 2 * a, "s_sl": c + a, "s_tp": c - 2 * a}
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
