"""Bollinger 20 / 2 breakouts outside a squeeze, broker days: the close crossing over the upper band goes long, under the lower band goes short, each with a 1 ATR 14 stop and 2 ATR target from the signal close; reversing.
Port of FMZ strategy #477945 "Multi Period Bollinger Bands Trend Breakout Strategy with Volatility Risk Control Model" (Bollinger Bands Breakout Strategy).

FMZ source id: 477945

Source
    https://www.fmz.com/strategy/477945 (PineScript v5, FMZ last modified 2025-01-10 15:12:13).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 89-147), BB 20 / 2; squeeze = width < half its SMA 20; ATR 14; R:R 2; risk 1 % position size
    crossover(close, upper) and not squeeze -> entry Long (qty from risk) + exit(limit = close + 2 atr, stop = close - atr);  crossunder(close, lower) and not squeeze -> entry Short + exit(mirror)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is sent on each signal bar from its close and ATR: the opening signal's levels are
      ported, sent as fractions of the fill open (a level at or through it is marketable and closed one
      bar late, as #458256); a second break of the same band inside a trade re-sends it, which is not
      followed (as #434428, mark trailing_stop_pending). REVERSAL INTENDED. Stop module:
      portfolio_kwargs {} (driver D4). Stops on daily bars: mark coarse_bar_stop. The risk-based qty is
      sizing. Daily bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ
      = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; signal-bar ATR bracket as fractions of the fill.
    2 generic: PASS, Bollinger breakouts outside a squeeze with an ATR bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: risk 1 % qty stored, not ported.
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

NAME = "fmz_477945_bb20_breakout_no_squeeze_atr_bracket_reversal"
FAMILY = "bollinger_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "length": [20, 50],
    "rr": [2.0, 3.0],
}
DEFAULT_PARAMS = {"length": 20, "rr": 2.0, "std_dev": 2.0, "atr_length": 14}


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
    n = int(p["length"])
    basis = c.rolling(n).mean()
    dev = float(p["std_dev"]) * c.rolling(n).std(ddof=0)
    up, dn = basis + dev, basis - dev
    width = up - dn
    squeeze = width < width.rolling(n).mean() * 0.5
    le = (c > up) & (c.shift(1) <= up.shift(1)) & ~squeeze
    se = (c < dn) & (c.shift(1) >= dn.shift(1)) & ~squeeze
    atr = _atr(bars_df, p["atr_length"])
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
