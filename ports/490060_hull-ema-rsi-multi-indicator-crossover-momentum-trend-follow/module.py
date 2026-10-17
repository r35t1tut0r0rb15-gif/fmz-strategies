"""Hull MA 12 crossing a lagged EMA 5 with RSI and two stochastic filters, with a two-bar swing stop and a 1.65 R
target, broker days: HMA 12 crossing above EMA 5 two bars back, with the close above both, RSI 14 > 50 and both
stochastic %K (12 and 5, smoothed 3) > 50 goes long, stopped at the lowest low of the previous two bars; shorts
mirrored.
Port of FMZ strategy #490060 "多指标交叉动量趋势追踪策略Hull与EMA结合RSI和双重随机震荡器的量化交易系统-Multi-Indicator-Crossover-Momentum-Trend-Following-Strategy-Quantitative-Trading-System-Combining-Hull-with-EMA-RSI-and-Dual-Stochastic-Oscillators" (TrendTwisterV1.5 (Forex Ready + Indicators)).

FMZ source id: 490060

Source
    https://www.fmz.com/strategy/490060 (PineScript v5, FMZ last modified 2025-04-11 11:13:55).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 182-230), HMA 12, EMA 5 [2], RSI 14, stochastic 12 / 5 smoothed 3, factor 1.65
    long = close > hma and close > ema[2] and rsi > 50 and k12 > 50 and k5 > 50 and crossover(hma, ema[2])
    short = the mirror (< 50, crossunder)
    on entry: exit(stop = lowest(low[1], 2), limit = close + (close - stop) x 1.65); shorts with highest(high[1], 2)

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.hma = WMA(2 x WMA(n/2) - WMA(n), round(sqrt(n))); ta.stoch(close, high, low, n) with windows including the
      current bar.
    * The bracket is placed on the signal bar from its levels: sl_stop = (close - stop) / close, tp_stop = 1.65 x
      that, shifted one bar inside stops(), re-based on the fill. A signal whose close is not beyond its stop (the
      stop would fire at once on the fill) emits no entry (a zero-length trade).
    * The commission in strategy() is a cost (not in the module). Entries reverse (REVERSAL INTENDED); a long and a
      short cannot fall on one bar.
    * Stop module: portfolio_kwargs {} (D4). Daily bars are broker days (17:00 America/New_York), stamped with their
      first minute; FREQ = "1D" from the backtest header: coarse_bar_stop.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at the signal bar.
    2 generic: PASS, moving averages, oscillators and swing levels.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity quoted; the bracket ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_490060_hull_ema_cross_rsi_stoch_swing_bracket"
FAMILY = "hull_ma"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "hma_len": [12, 20],
    "profit_factor": [1.65, 3.0],
}
DEFAULT_PARAMS = {"hma_len": 12, "ema_len": 5, "rsi_len": 14, "profit_factor": 1.65, "stop_bars": 2}


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
    r = r.where(up != 0, 0.0)
    return r.where(dn != 0, 100.0).where(up.notna() & dn.notna())


def _wma(x, n):
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda a: np.dot(a, w) / w.sum(), raw=True)


def _hma(x, n):
    return _wma(2 * _wma(x, max(int(n / 2), 1)) - _wma(x, n), max(int(round(np.sqrt(n))), 1))


def _stoch(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    rng = hh - ll
    return (100 * (c - ll) / rng).where(rng != 0)


def _setup(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    hma = _hma(c, int(p["hma_len"]))
    ema2 = c.ewm(span=int(p["ema_len"]), adjust=False).mean().shift(2)
    rsi = _rsi(c, int(p["rsi_len"]))
    k1, k2 = _stoch(bars_df, 12).rolling(3).mean(), _stoch(bars_df, 5).rolling(3).mean()
    up = (hma > ema2) & (hma.shift(1) <= ema2.shift(1))
    dn = (hma < ema2) & (hma.shift(1) >= ema2.shift(1))
    long_c = (c > hma) & (c > ema2) & (rsi > 50) & (k1 > 50) & (k2 > 50) & up
    short_c = (c < hma) & (c < ema2) & (rsi < 50) & (k1 < 50) & (k2 < 50) & dn
    nb = int(p["stop_bars"])
    d_long = (c - lo.shift(1).rolling(nb).min()) / c
    d_short = (h.shift(1).rolling(nb).max() - c) / c
    long_c = long_c & (d_long > 0)
    short_c = short_c & (d_short > 0)
    dist = d_long.where(long_c, d_short.where(short_c))
    return long_c.fillna(False).astype(bool), short_c.fillna(False).astype(bool), dist


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    long_c, short_c, _ = _setup(bars_df, p)
    false = pd.Series(False, index=bars_df.index)
    return long_c, false, short_c, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, _, dist = _setup(bars_df, p)
    return {"sl_stop": dist.shift(1), "tp_stop": (p["profit_factor"] * dist).shift(1)}


def portfolio_kwargs(**params):
    return {}
