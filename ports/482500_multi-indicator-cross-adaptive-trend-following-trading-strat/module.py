"""EMA 6 / 20 crossings with the close on the matching side of a 333-bar least-squares line and RSI 14 on the 50 side, broker days: each side enters with a 1 % stop and a 2 % target from the signal close; reversing.
Port of FMZ strategy #482500 "Multi Indicator Cross Adaptive Trend Following Trading Strategy" (EMA 6-20 + LSMA 333 + RSI 50 Filtreli Al-Sat Stratejisi).

FMZ source id: 482500

Source
    https://www.fmz.com/strategy/482500 (PineScript v6, FMZ last modified 2025-02-18 17:17:25).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 112-162), EMA 6 / 20; LSMA linreg(close, 333, 0); RSI 14; stop 1 %, target 2 %
    crossover(ema6, ema20) and close > lsma and rsi > 50 -> entry Long + exit(stop = close x 0.99, limit = close x 1.02);  mirror -> entry Short + exit(stop = close x 1.01, limit = close x 0.98)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The levels are fixed at the signal close and sent as fractions of the fill open (a level at or
      through it is marketable and closed one bar late, as #458256). A filtered-out opposite crossing can
      leave a long held into the next up-crossing, which re-sends the bracket from the new close; stops()
      keeps the first, so the repeat case is marked trailing_stop_pending (as #434428). REVERSAL INTENDED.
      Stop module: portfolio_kwargs {} (driver D4). Stops on daily bars: mark coarse_bar_stop. No sizing
      code. Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; percent bracket from the signal close as fractions of the fill.
    2 generic: PASS, EMA crossings with a long regression-line side and RSI filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
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

NAME = "fmz_482500_ema6_20_cross_lsma333_rsi50_pct_bracket_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "stop_loss_perc": [1.0, 3.0],
    "take_profit_perc": [2.0, 6.0],
}
DEFAULT_PARAMS = {"stop_loss_perc": 1.0, "take_profit_perc": 2.0, "ema_short": 6, "ema_long": 20,
                  "lsma_length": 333, "rsi_length": 14}


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


def _linreg(x, n):
    """Pine ta.linreg(x, n, 0): the least-squares line over the last n values, at the last one."""
    v = x.to_numpy(dtype=float)
    m = len(v)
    out = np.full(m, np.nan)
    if m >= n:
        k = np.arange(n, dtype=float)
        sy = np.convolve(v, np.ones(n))[:m]                        # sum of the window
        sky = np.convolve(v, k)[:m]                                # sum of (age) x value
        sxy = (n - 1) * sy - sky                                   # x = n - 1 - age
        sx, sxx = k.sum(), (k * k).sum()
        b = (n * sxy - sx * sy) / (n * sxx - sx * sx)
        a = (sy - b * sx) / n
        out[n - 1:] = (a + b * (n - 1))[n - 1:]
    return pd.Series(out, index=x.index)


def _signals(bars_df, p):
    c = bars_df["close"]
    f = c.ewm(span=int(p["ema_short"]), adjust=False).mean()
    s = c.ewm(span=int(p["ema_long"]), adjust=False).mean()
    ls = _linreg(c, int(p["lsma_length"]))
    r = _rsi(c, int(p["rsi_length"]))
    le = (f > s) & (f.shift(1) <= s.shift(1)) & (c > ls) & (r > 50)
    se = (f < s) & (f.shift(1) >= s.shift(1)) & (c < ls) & (r < 50)
    sl, tp = float(p["stop_loss_perc"]) / 100, float(p["take_profit_perc"]) / 100
    lvl = {"l_sl": c * (1 - sl), "l_tp": c * (1 + tp), "s_sl": c * (1 + sl), "s_tp": c * (1 - tp)}
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
