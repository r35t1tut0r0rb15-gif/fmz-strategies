"""EMA-14-smoothed RSI 14 crossings of 70 and 30, broker days: crossing over either level goes long, crossing under either goes short, each with a 1 ATR 14 stop and target from the signal close; reversing.
Port of FMZ strategy #477608 "基于EMA平滑RSI和ATR动态止盈止损的多时序量化交易策略-Multi-Timeframe-Quantitative-Trading-Strategy-Based-on-EMA-Smoothed-RSI-and-ATR-Dynamic-Stop-Loss-Take-Profit" (RSI Trading Strategy with EMA and ATR Stop Loss/Take Profit).

FMZ source id: 477608

Source
    https://www.fmz.com/strategy/477608 (PineScript v6, FMZ last modified 2025-01-06 16:43:14).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 90-158), RSI 14, EMA 14 smoothing; levels 30 / 70; ATR 14 x 1
    crossover(srsi, 70) or crossover(srsi, 30) -> entry Long + exit(stop = close - atr, limit = close + atr);  crossunder(srsi, 70) or crossunder(srsi, 30) -> entry Short + exit(mirror)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is sent on each signal bar from its close and ATR: the opening signal's levels are
      ported, sent as fractions of the fill open (a level at or through it is marketable and closed one
      bar late, as #458256); a long can see a second up-crossing (30, then 70) that re-sends it, which is
      not followed (as #434428, mark trailing_stop_pending). The crossing counter and table only draw.
      REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). Stops on daily bars: mark
      coarse_bar_stop. No sizing code. Daily bars are broker days (17:00 America/New_York), stamped with
      their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; signal-bar ATR bracket as fractions of the fill.
    2 generic: PASS, smoothed RSI level crossings with an ATR bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the ATR multiplier stored.
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

NAME = "fmz_477608_ema_smoothed_rsi14_level_cross_atr_bracket_reversal"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "smoothing": [14, 5],
    "atr_mult": [1.0, 2.0],
}
DEFAULT_PARAMS = {"smoothing": 14, "atr_mult": 1.0, "rsi_length": 14, "atr_length": 14}


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
    sr = _rsi(c, int(p["rsi_length"])).ewm(span=int(p["smoothing"]), adjust=False).mean()

    def up(lv):
        return (sr > lv) & (sr.shift(1) <= lv)

    def dn(lv):
        return (sr < lv) & (sr.shift(1) >= lv)

    le = up(70.0) | up(30.0)
    se = dn(70.0) | dn(30.0)
    a = _atr(bars_df, p["atr_length"]) * float(p["atr_mult"])
    lvl = {"l_sl": c - a, "l_tp": c + a, "s_sl": c + a, "s_tp": c - a}
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
