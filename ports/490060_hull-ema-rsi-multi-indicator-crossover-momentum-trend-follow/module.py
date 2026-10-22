"""HMA 12 crossings of the EMA 5 taken two bars back, with RSI 14 and two smoothed stochastics (12 and 5) on the same side of 50, broker days: the up-cross goes long with a stop at the prior 2-bar low and a 1.65 R target, the down-cross goes short with the mirror; reversing.
Port of FMZ strategy #490060 "多指标交叉动量趋势追踪策略Hull与EMA结合RSI和双重随机震荡器的量化交易系统-Multi-Indicator-Crossover-Momentum-Trend-Following-Strategy-Quantitative-Trading-System-Combining-Hull-with-EMA-RSI-and-Dual-Stochastic-Oscillators" (TrendTwisterV1.5 (Forex Ready + Indicators)).

FMZ source id: 490060

Source
    https://www.fmz.com/strategy/490060 (PineScript v5, FMZ last modified 2025-04-11 11:13:55).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 178-241), HMA 12; EMA 5 [2]; RSI 14; stoch 12 / 5 (SMA 3); stop = lowest(low[1], 2); RR 1.65; 10 % of equity, commission 0.01 %
    crossover(hma, ema5[2]) and close > both and rsi > 50 and both stochs > 50 -> entry Long + exit(stop = lowest(low[1], 2), limit = close + 1.65 (close - stop));  mirror -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The HMA is wma(2 x wma(close, 6) - wma(close, 12), 3). The bracket is set on the signal bar and sent as
      fractions of the fill open (a level at or through it is marketable and closed one bar late, as
      #458256). A later same-side crossing while held re-sends the bracket; the port keeps the opening
      levels, mark trailing_stop_pending (as #434428). An entry on the other side reverses (REVERSAL
      INTENDED). Stop module: portfolio_kwargs {} (driver D4). Stops on daily bars: mark coarse_bar_stop.
      Daily bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from
      the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; swing bracket as fractions of the fill.
    2 generic: PASS, HMA / shifted-EMA crossings with RSI and stochastic filters.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: 10 % of equity and commission stored, not ported.
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

NAME = "fmz_490060_hma12_ema5_shift2_cross_rsi_stoch_swing_bracket_reversal"
FAMILY = "hull_ma"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "hmaLength": [12, 20],
    "profitFactor": [1.65, 3.0],
}
DEFAULT_PARAMS = {"hmaLength": 12, "profitFactor": 1.65, "emaLength": 5}


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


def _wma(x, n):
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda a: a @ w / w.sum(), raw=True)


def _signals(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["hmaLength"])
    hma = _wma(2 * _wma(c, n // 2) - _wma(c, n), int(np.floor(np.sqrt(n))))
    es = c.ewm(span=int(p["emaLength"]), adjust=False).mean().shift(2)
    r = _rsi(c, 14)

    def stoch(k):
        hh, ll = h.rolling(k).max(), lo.rolling(k).min()
        return (100 * (c - ll) / (hh - ll).where(hh > ll)).rolling(3).mean()

    k1, k2 = stoch(12), stoch(5)
    le = ((hma > es) & (hma.shift(1) <= es.shift(1)) & (c > hma) & (c > es) & (r > 50)
          & (k1 > 50) & (k2 > 50))
    se = ((hma < es) & (hma.shift(1) >= es.shift(1)) & (c < hma) & (c < es) & (r < 50)
          & (k1 < 50) & (k2 < 50))
    ls, ss = lo.shift(1).rolling(2).min(), h.shift(1).rolling(2).max()
    pf = float(p["profitFactor"])
    lvl = {"l_sl": ls, "l_tp": c + (c - ls) * pf, "s_sl": ss, "s_tp": c - (ss - c) * pf}
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
