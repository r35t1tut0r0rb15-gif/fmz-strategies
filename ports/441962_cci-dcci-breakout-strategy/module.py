"""CCI 100 re-entries on the WMA side with a wide ATR bracket, broker days: the close above the WMA 5 with the CCI 16 crossing back over -100 goes long, the close under it with the CCI crossing back under
100 short; a stop 10 ATR(14) from the entry and a target 1.5 times the stop distance; reversing.
Port of FMZ strategy #441962 "动态CCI突破策略DCCI-Breakout-Strategy" (CCI Scalping Strat).

FMZ source id: 441962

Source
    https://www.fmz.com/strategy/441962 (PineScript v4, FMZ last modified 2024-02-18 10:13:21).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 186-301), direction all; CCI 16, WMA 5; stop type ATR (14 x 10); take profit RR 1.5; direct reverse allowed; reverse off; 100 % of equity, capital 10000, commission 0.04
    BUY = close > wma5 and crossover(cci16, -100) -> entry long;  SELL = close < wma5 and crossunder(cci16, 100) -> entry short
    ATRLongStop = valuewhen(position changed, ohlc4 - 10 atr(14), 0);  TP = avg + (avg - stop) 1.5;  strategy.exit(limit = TP, stop = SL) for each side (shorts mirrored)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The script's stop is ohlc4 - 10 ATR(14) of the bar where the position changed (the fill bar), placed
      at that bar's close; the port sets sl = 10 ATR(14) / close and tp = 1.5 sl from the signal bar,
      shifted one bar inside stops() and re-based on the fill, active from the fill bar (stated
      approximation, as #440797). strategy.entry reverses (direct reverse on): REVERSAL INTENDED. Stop
      module: portfolio_kwargs {} (driver D4). Stops on daily bars: mark coarse_bar_stop. The 100 % of
      equity size, capital and commission are sizing. Daily bars are broker days (17:00 America/New_York),
      stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket from signal-bar data (approximation stated).
    2 generic: ADAPT, fill-bar ATR stop -> signal-bar ATR multiple.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size, capital and commission stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND438012 (2 members, best partner #438012, Jaccard 0.687); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_441962_cci16_100_reentry_wma_side_atr_bracket"
FAMILY = "momentum_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "cci_len": [16, 20],
    "atr_mult": [10.0, 5.0],
}
DEFAULT_PARAMS = {"cci_len": 16, "atr_mult": 10.0, "wma_len": 5, "atr_len": 14, "rr": 1.5}


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


def _wma(x, n):
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda a: np.dot(a, w) / w.sum(), raw=True)


def _cci(x, n):
    ma = x.rolling(n).mean()
    md = x.rolling(n).apply(lambda a: np.abs(a - a.mean()).mean(), raw=True)
    return (x - ma) / (0.015 * md)


def _fractions(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    sl = float(p["atr_mult"]) * _rma(tr, int(p["atr_len"])) / c
    return sl, float(p["rr"]) * sl


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    cci = _cci(c, int(p["cci_len"]))
    w = _wma(c, int(p["wma_len"]))
    lsig = ((c > w) & (cci > -100) & (cci.shift(1) <= -100)).to_numpy()
    ssig = ((c < w) & (cci < 100) & (cci.shift(1) >= 100)).to_numpy()
    sl_s, tp_s = _fractions(bars_df, p)
    sl, tp = sl_s.to_numpy(), tp_s.to_numpy()
    ov = bars_df["open"].to_numpy(dtype=float)
    hv, lv = h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    m = len(ov)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, entry_i, s_, t_ = 0, -1, np.nan, np.nan
    for i in range(m):
        if pos != 0 and i >= entry_i:
            x = ov[entry_i]
            if pos == 1 and (lv[i] <= x * (1 - s_) or hv[i] >= x * (1 + t_)):
                pos = 0
            elif pos == -1 and (hv[i] >= x * (1 + s_) or lv[i] <= x * (1 - t_)):
                pos = 0
        if i + 1 < m and not np.isnan(sl[i]):
            if lsig[i] and pos != 1:
                le[i], pos, entry_i, s_, t_ = True, 1, i + 1, sl[i], tp[i]
            elif ssig[i] and pos != -1:
                se[i], pos, entry_i, s_, t_ = True, -1, i + 1, sl[i], tp[i]
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    sl, tp = _fractions(bars_df, p)
    return {"sl_stop": sl.shift(1), "tp_stop": tp.shift(1)}


def portfolio_kwargs(**params):
    return {}
