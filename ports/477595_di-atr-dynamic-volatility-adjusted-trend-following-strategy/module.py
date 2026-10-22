"""DI 14 dominance by 20 points with the close on the SMA 20 side, broker days: DI+ over DI- by 20 with the close above goes long, the mirror goes short, each with a 1.5 ATR stop and 2.5 ATR target from the signal close; reversing.
Port of FMZ strategy #477595 "基于DI指标的动态波动率趋势跟踪策略结合ATR止盈止损体系-Dynamic-Volatility-Adjusted-Trend-Following-Strategy-Based-on-DI-Indicators-with-ATR-Stop-Management" (使用 DI+ 和 DI- 的策略).

FMZ source id: 477595

Source
    https://www.fmz.com/strategy/477595 (PineScript v5, FMZ last modified 2025-01-06 16:18:01).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 105-182), DMI 14 / 14; SMA 20; strength 20; ATR 14 x 1.5 stop, x 2.5 target
    di+ > di- + 20 and close > sma20 -> entry 多單, stop := close - 1.5 atr, tp := close + 2.5 atr;  mirror -> entry 空單 with the mirror levels
    in a position and time > entry_bar_index -> exit(stop, limit) from the stored levels

Interpretation choices (Pine rules in SURVEY_README.md)
    * The entry_bar_index guard compares a bar number with a timestamp and always passes, so the exit is
      sent on every bar of a position from the stored levels. The conditions are states: every repeat
      signal re-stores the levels from its close; the opening signal's levels are ported, sent as
      fractions of the fill open (a level at or through it is marketable and closed one bar late, as
      #458256), and the repeat re-sends are not followed (as #434428, mark trailing_stop_pending).
      REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). Stops on daily bars: mark
      coarse_bar_stop. No sizing code. Daily bars are broker days (17:00 America/New_York), stamped with
      their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; signal-bar ATR bracket as fractions of the fill.
    2 generic: PASS, DI dominance with an SMA filter and an ATR bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the ATR bracket inputs stored.
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

NAME = "fmz_477595_di14_dominance20_sma20_atr_bracket_reversal"
FAMILY = "adx_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "strength": [20, 10],
    "tp_mult": [2.5, 4.0],
}
DEFAULT_PARAMS = {"strength": 20, "tp_mult": 2.5, "sl_mult": 1.5, "di_length": 14, "sma_length": 20, "atr_length": 14}


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
    plus, minus, _ = _dmi(bars_df, int(p["di_length"]))
    ma = c.rolling(int(p["sma_length"])).mean()
    st = float(p["strength"])
    le = (plus > minus + st) & (c > ma)
    se = (minus > plus + st) & (c < ma)
    atr = _atr(bars_df, p["atr_length"])
    sl, tp = float(p["sl_mult"]), float(p["tp_mult"])
    lvl = {"l_sl": c - sl * atr, "l_tp": c + tp * atr, "s_sl": c + sl * atr, "s_tp": c - tp * atr}
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
