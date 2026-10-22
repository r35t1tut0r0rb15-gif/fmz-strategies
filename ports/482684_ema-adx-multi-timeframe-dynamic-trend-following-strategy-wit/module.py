"""EMA 50 / 200 crossings with ADX 14 over 25 and an RSI 14 filter, broker days: the cross up with RSI over 30 goes long, the cross down with RSI under 70 goes short, each with a 3 % target and a 3 % stop from the signal close; RSI over 70 closes a long, under 30 a short; reversing.
Port of FMZ strategy #482684 "多重时间框架动态趋势跟踪策略结合EMA与ADX指标-Multi-Timeframe-Dynamic-Trend-Following-Strategy-with-EMA-and-ADX-Integration" (DOGE Enhanced Trend Following Strategy).

FMZ source id: 482684

Source
    https://www.fmz.com/strategy/482684 (PineScript v5, FMZ last modified 2025-02-27 17:52:45).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 88-144), EMA 50 / 200; DMI 14 / 14, ADX > 25; RSI 14, 70 / 30; TP x 1.03, SL x 0.97; 5 % of equity, commission 0.1, slippage 2
    crossover(ema50, ema200) and adx > 25 and rsi > 30 -> entry Long + exit(limit = close x 1.03, stop = close x 0.97);  mirror (rsi < 70) -> entry Short + exit(limit = close x 0.97, stop = close x 1.03)
    strategy.close("Long", when = rsi > 70);  strategy.close("Short", when = rsi < 30)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "240" EMAs are requested but feed no condition. The levels are fixed at the signal close and sent
      as fractions of the fill open (a level at or through it is marketable and closed one bar late, as
      #458256). A filtered-out opposite crossing can leave a position held into a repeat crossing, which
      re-sends the bracket from the new close; stops() keeps the first, so the repeat case is marked
      trailing_stop_pending (as #434428), and an RSI close on that repeat bar is dropped. REVERSAL
      INTENDED. Stop module: portfolio_kwargs {} (driver D4). Stops on daily bars: mark coarse_bar_stop.
      The 5 % of equity size is sizing; commission and slippage are costs and are not ported (house cost
      model). Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; percent bracket from the signal close as fractions of the fill.
    2 generic: PASS, EMA crossings with ADX and RSI filters and RSI exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 5 % of equity stored, not ported; commission and slippage not ported.
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

NAME = "fmz_482684_ema50_200_cross_adx25_rsi_pct3_bracket_rsi_exit_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "adx_threshold": [25, 20],
    "bracket_frac": [0.03, 0.06],
}
DEFAULT_PARAMS = {"adx_threshold": 25, "bracket_frac": 0.03, "rsi_overbought": 70, "rsi_oversold": 30,
                  "ema_fast": 50, "ema_slow": 200, "adx_length": 14, "rsi_length": 14}


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


def _fixnan(x):
    """Pine fixnan: the last non-NaN value, NaN before the first."""
    v = x.to_numpy(dtype=float)
    idx = np.where(~np.isnan(v), np.arange(len(v)), 0)
    idx = np.maximum.accumulate(idx)
    return pd.Series(v[idx], index=x.index)


def _dmi(b, n):
    h, lo, c = b["high"], b["low"], b["close"]
    up, dn = h.diff(), -lo.diff()
    pdm = up.where((up > dn) & (up > 0), 0.0).where(up.notna())
    mdm = dn.where((dn > up) & (dn > 0), 0.0).where(dn.notna())
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1).where(pc.notna())
    trr = _rma(tr, n)
    plus = _fixnan(100 * _rma(pdm, n) / trr)
    minus = _fixnan(100 * _rma(mdm, n) / trr)
    s = plus + minus
    adx = 100 * _rma((plus - minus).abs() / s.where(s != 0, 1.0), n)
    return plus, minus, adx


def _signals(bars_df, p):
    c = bars_df["close"]
    f = c.ewm(span=int(p["ema_fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["ema_slow"]), adjust=False).mean()
    adx = _dmi(bars_df, int(p["adx_length"]))[2]
    r = _rsi(c, int(p["rsi_length"]))
    strong = adx > float(p["adx_threshold"])
    le = (f > s) & (f.shift(1) <= s.shift(1)) & strong & (r > float(p["rsi_oversold"]))
    se = (f < s) & (f.shift(1) >= s.shift(1)) & strong & (r < float(p["rsi_overbought"]))
    k = float(p["bracket_frac"])
    lvl = {"l_sl": c * (1 - k), "l_tp": c * (1 + k), "s_sl": c * (1 + k), "s_tp": c * (1 - k)}
    return le, se, lvl, r


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl, r = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    sf = se.shift(1, fill_value=False)
    l_thr = (lvl["l_sl"].shift(1) >= o) | (lvl["l_tp"].shift(1) <= o)    # marketable at the fill
    s_thr = (lvl["s_sl"].shift(1) <= o) | (lvl["s_tp"].shift(1) >= o)
    lx = (lf & l_thr) | (r > float(p["rsi_overbought"]))
    sx = (sf & s_thr) | (r < float(p["rsi_oversold"]))
    return le, lx & ~se & ~le, se, sx & ~le & ~se


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl, r = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    sl_f = (1 - lvl["l_sl"].shift(1) / o).where(lf, lvl["s_sl"].shift(1) / o - 1)
    tp_f = (lvl["l_tp"].shift(1) / o - 1).where(lf, 1 - lvl["s_tp"].shift(1) / o)
    return {"sl_stop": sl_f.where(sl_f > 0), "tp_stop": tp_f.where(tp_f > 0)}


def portfolio_kwargs(**params):
    return {}
