"""Close crossings out of the Keltner channel (EMA 20 +/- 2 ATR 20) on the side of the EMA 200 with RSI 14 over (under) 50, broker days: the break up goes long, the break down goes short, each with a 1.5 ATR 14 stop and a 2 ATR target from the signal close; a close back through the EMA 20 closes; reversing.
Port of FMZ strategy #488883 "Advanced Dynamic Range Breakout Trend Following Strategy" (Enhanced Keltner Channel Strategy).

FMZ source id: 488883

Source
    https://www.fmz.com/strategy/488883 (PineScript v5, FMZ last modified 2025-03-31 15:43:43).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 190-246), Keltner EMA 20, ATR 20 x 2; EMA 200; RSI 14; SL 1.5 ATR 14; TP 2 ATR 14
    crossover(close, upper) and close > ema200 and rsi > 50 -> entry Long + exit(stop = close - 1.5 atr, limit = close + 2 atr);  mirror -> entry Short
    crossunder(close, ema20) -> close Long;  crossover(close, ema20) -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is set on the signal bar from its close and sent as fractions of the fill open (a level
      at or through it is marketable and closed one bar late, as #458256). A later same-side breakout while
      held re-sends the bracket; the port keeps the opening levels, mark trailing_stop_pending (as
      #434428). An entry on the other side reverses (REVERSAL INTENDED). Stop module: portfolio_kwargs {}
      (driver D4). Stops on daily bars: mark coarse_bar_stop. No sizing code. Daily bars are broker days
      (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; ATR bracket as fractions of the fill.
    2 generic: PASS, Keltner breakouts with trend / RSI filters, ATR bracket and EMA exit.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_488883_keltner20_2_breakout_ema200_rsi_atr_bracket_ema_exit_reversal"
FAMILY = "keltner_channel"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "mult": [2.0, 1.5],
    "length": [20, 30],
}
DEFAULT_PARAMS = {"mult": 2.0, "length": 20, "trendEMA": 200, "rsiLength": 14}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])

    def ema(x, k):
        return x.ewm(span=int(k), adjust=False).mean()

    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]
    e = ema(c, n)
    a20 = _rma(tr, n)
    upper, lower = e + float(p["mult"]) * a20, e - float(p["mult"]) * a20
    e200 = ema(c, p["trendEMA"])
    r = _rsi(c, int(p["rsiLength"]))
    le = (c > upper) & (pc <= upper.shift(1)) & (c > e200) & (r > 50)
    se = (c < lower) & (pc >= lower.shift(1)) & (c < e200) & (r < 50)
    lx = (c < e) & (pc >= e.shift(1))
    sx = (c > e) & (pc <= e.shift(1))
    a14 = _rma(tr, 14)
    lvl = {"l_sl": c - 1.5 * a14, "l_tp": c + 2 * a14, "s_sl": c + 1.5 * a14, "s_tp": c - 2 * a14}
    return le, lx, se, sx, lvl


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx, se, sx, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf, sf = le.shift(1, fill_value=False), se.shift(1, fill_value=False)
    l_thr = lf & ((lvl["l_sl"].shift(1) >= o) | (lvl["l_tp"].shift(1) <= o))    # marketable at the fill
    s_thr = sf & ((lvl["s_sl"].shift(1) <= o) | (lvl["s_tp"].shift(1) >= o))
    return le, (lx | l_thr) & ~le & ~se, se, (sx | s_thr) & ~se & ~le


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx, se, sx, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    l_sl, l_tp = 1 - lvl["l_sl"].shift(1) / o, lvl["l_tp"].shift(1) / o - 1
    s_sl, s_tp = lvl["s_sl"].shift(1) / o - 1, 1 - lvl["s_tp"].shift(1) / o
    sl = l_sl.where(lf, s_sl)
    tp = l_tp.where(lf, s_tp)
    return {"sl_stop": sl.where(sl > 0), "tp_stop": tp.where(tp > 0)}


def portfolio_kwargs(**params):
    return {}
