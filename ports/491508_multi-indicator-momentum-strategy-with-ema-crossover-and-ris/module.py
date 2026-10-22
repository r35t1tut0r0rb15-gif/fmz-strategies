"""EMA 9 / 21 crossings with RSI 14 on the same side of 50 and the MACD side, broker days: the up-cross goes long, the down-cross goes short, each with a 1 % stop and 2 % target from the signal close; reversing.
Port of FMZ strategy #491508 "Multi Indicator Momentum Strategy with EMA Crossover and Risk Management" (Estrategia EMAs + RSI + MACD con SL y TP).

FMZ source id: 491508

Source
    https://www.fmz.com/strategy/491508 (PineScript v5, FMZ last modified 2025-04-21 16:00:38).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 196-242), EMA 9 / 21; RSI 14 / 50; MACD 12 / 26 / 9; SL 1 %, TP 2 %; 10 % of equity
    crossover(ema9, ema21) and rsi > 50 and macd > signal -> entry Compra + exit(stop = close x 0.99, limit = close x 1.02);  mirror -> entry Venta

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is set on the signal bar from its close and sent as fractions of the fill open (a level
      at or through it is marketable and closed one bar late, as #458256). A later same-side crossing while
      held re-sends the bracket; the port keeps the opening levels, mark trailing_stop_pending (as #434428).
      An entry on the other side reverses (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (driver D4).
      Stops on daily bars: mark coarse_bar_stop. Daily bars are broker days (17:00 America/New_York),
      stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; percent bracket as fractions of the fill.
    2 generic: PASS, EMA crossings with RSI / MACD confirmation and a percent bracket.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: 10 % of equity stored, not ported.
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

NAME = "fmz_491508_ema9_21_cross_rsi_macd_sl1_tp2pct_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "slPercent": [1.0, 2.0],
    "tpPercent": [2.0, 4.0],
}
DEFAULT_PARAMS = {"slPercent": 1.0, "tpPercent": 2.0}


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

    def ema(n):
        return c.ewm(span=int(n), adjust=False).mean()

    f, s = ema(9), ema(21)
    r = _rsi(c, 14)
    macd = ema(12) - ema(26)
    sig = macd.ewm(span=9, adjust=False).mean()
    le = (f > s) & (f.shift(1) <= s.shift(1)) & (r > 50) & (macd > sig)
    se = (f < s) & (f.shift(1) >= s.shift(1)) & (r < 50) & (macd < sig)
    sl, tp = float(p["slPercent"]) / 100, float(p["tpPercent"]) / 100
    lvl = {"l_sl": c * (1 - sl), "l_tp": c * (1 + tp), "s_sl": c * (1 + sl), "s_tp": c * (1 - tp)}
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
