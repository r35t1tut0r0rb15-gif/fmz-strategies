"""EMA 10 / 39 crossings filtered by the EMA 73 and a daily EMA 143, 2-day bars: the cross up with the close over both goes long, the cross down under both goes short; reversing. Each trade has a 1 ATR stop and 2 ATR target from its signal close.
Port of FMZ strategy #473412 "多重指数均线交叉战略结合交易量ATR动态止损优化策略-Multi-Exponential-Moving-Average-Crossover-Strategy-with-Volume-Based-ATR-Dynamic-Stop-Loss-Optimization" (Enhanced EMA Crossover Strategy).

FMZ source id: 473412

Source
    https://www.fmz.com/strategy/473412 (PineScript v5, FMZ last modified 2024-11-29 17:06:37).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 88-131), EMA 10 / 39 / 73; "D" EMA 143; ATR 14; target 2 ATR, stop 1 ATR from the signal close
    crossover(ema10, ema39) and close > ema73 and close > ema143(D) -> entry Long, exit(limit = close + 2 atr, stop = close - atr);  crossunder and below both -> entry Short, exit(limit = close - 2 atr, stop = close + atr)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "D" request is a LOWER time frame than the 2-day chart; without lookahead it returns the chart
      bar's last daily bar (as #436765): the EMA 143 of broker-day closes on the block's last day, built
      in precompute. The bracket is sent once, on the signal bar, from its close and ATR: sent as
      fractions of the fill open; a level at or through it is marketable and closed one bar late (as
      #458256). Crossings alternate, so no repeat signal re-sends it. REVERSAL INTENDED. Stop module:
      portfolio_kwargs {} (driver D4). Stops on 2-day bars: mark coarse_bar_stop. No sizing code. FREQ =
      "2D" from the backtest header (blocks of 2 broker days, as #429148).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the daily EMA from the block's last day; signal-bar ATR bracket.
    2 generic: PASS, EMA crossings with trend filters and an ATR bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (1 trial), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_473412_ema10_39_cross_ema73_daily143_atr_bracket_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2D"  # backtest header period: 2d (blocks of 2 broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {}
DEFAULT_PARAMS = {"days": 2}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    p = {**DEFAULT_PARAMS, **params}
    days = int(p["days"])
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    key = np.asarray((lab - pd.Timestamp("1970-01-01")).days // days)
    bars = df.groupby(key).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(key).first()
    # the daily EMA 143 of broker-day closes, read on each block's last broker day
    dclose = df["close"].groupby(lab).last()
    dema = dclose.ewm(span=143, adjust=False).mean()
    dkey = np.asarray((dema.index - pd.Timestamp("1970-01-01")).days // days)
    bars["ema_d"] = dema.groupby(dkey).last().reindex(bars.index).to_numpy()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)
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
    a, b, f = (c.ewm(span=n, adjust=False).mean() for n in (10, 39, 73))
    d = bars_df["ema_d"]
    le = (a > b) & (a.shift(1) <= b.shift(1)) & (c > f) & (c > d)
    se = (a < b) & (a.shift(1) >= b.shift(1)) & (c < f) & (c < d)
    atr = _atr(bars_df, 14)
    lvl = {"l_sl": c - atr, "l_tp": c + 2 * atr, "s_sl": c + atr, "s_tp": c - 2 * atr}
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
