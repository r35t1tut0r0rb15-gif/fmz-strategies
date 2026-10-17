"""LazyBear-style Impulse MACD crosses on the side of an EMA 200, broker days: with the close above the EMA, an impulse line
crossing above its SMA 9 while both are below zero goes long; with the close below it, a cross down while both are above
zero goes short (reversing). The stop is the 20-bar low (high) and the target 1.5 times that distance.
Port of FMZ strategy #434715 "基于指数移动平均线和MACD指标的量化交易策略Strategy-Based-on-Exponential-Moving-Average-and-MACD-Indicator" (Strategia EMA + Impulse MACD).

FMZ source id: 434715

Source
    https://www.fmz.com/strategy/434715 (PineScript v4, FMZ last modified 2023-12-08 17:04:03).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 195-268), EMA 200; impulse MACD 34 (SMMA of high / low, ZLEMA of hlc3), signal 9; stop look back 20, target 1.5 R
    imp = zlema(hlc3, 34) > smma(high, 34) ? zlema - smma(high) : zlema < smma(low, 34) ? zlema - smma(low) : 0;  sig = sma(imp, 9)
    close > ema200 and imp < 0 and sig < 0 and crossover(imp, sig) -> entry long;  mirror -> entry short
    exit long (stop = lowest(low, 20), limit = close + (close - lowest) 1.5)   (re-issued every bar);  shorts mirror

Interpretation choices (Pine rules in SURVEY_README.md)
    * The calculations sit inside "bar_index >=" blocks, which only delay their start (warm-up). The
      SMMA starts from its SMA, the ZLEMA is 2 EMA - EMA(EMA).
    * The exits are re-issued every bar at that bar's 20-bar extreme and close, so the levels move
      after entry: stops() cannot express that (mark trailing_stop_pending). The port fixes the
      signal bar's levels as fractions of its close, shifted one bar inside stops() (re-based on the
      fill); a signal whose stop is not beyond the close places no entry.
    * strategy.entry reverses: REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). Stops
      on daily bars: mark coarse_bar_stop. Daily bars are broker days (17:00 America/New_York),
      stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; re-issued levels fixed at entry (approximation stated).
    2 generic: PASS, an impulse MACD, an average side and swing exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: trailing_stop_pending, coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_434715_impulse_macd_ema200_bracket"
FAMILY = "macd_cross"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "len_ma": [34, 20],
    "rr": [1.5, 3.0],
}
DEFAULT_PARAMS = {"ema_len": 200, "len_ma": 34, "len_sig": 9, "stop_len": 20, "rr": 1.5}


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


def _smma(x, n):
    v = x.to_numpy(dtype=float)
    sma = x.rolling(n).mean().to_numpy()
    out = np.full(len(v), np.nan)
    for i in range(len(v)):
        if i > 0 and not np.isnan(out[i - 1]):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
        else:
            out[i] = sma[i]
    return out


def _setup(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["len_ma"])
    ema200 = c.ewm(span=int(p["ema_len"]), adjust=False).mean().to_numpy()
    hi, lw = _smma(h, n), _smma(lo, n)
    src = (h + lo + c) / 3
    e1 = src.ewm(span=n, adjust=False).mean()
    mi = (2 * e1 - e1.ewm(span=n, adjust=False).mean()).to_numpy()
    with np.errstate(invalid="ignore"):
        imp = np.where(mi > hi, mi - hi, np.where(mi < lw, mi - lw, 0.0))
    imp[np.isnan(hi) | np.isnan(lw)] = np.nan
    imp_s = pd.Series(imp, index=c.index)
    sig = imp_s.rolling(int(p["len_sig"])).mean()
    cv = c.to_numpy(dtype=float)
    xu = ((imp_s > sig) & (imp_s.shift(1) <= sig.shift(1))).to_numpy()
    xd = ((imp_s < sig) & (imp_s.shift(1) >= sig.shift(1))).to_numpy()
    iv, sv = imp, sig.to_numpy()
    k = int(p["stop_len"])
    ll, hh = lo.rolling(k).min().to_numpy(), h.rolling(k).max().to_numpy()
    with np.errstate(invalid="ignore"):
        l_sl, s_sl = (cv - ll) / cv, (hh - cv) / cv
        le = (cv > ema200) & (iv < 0) & (sv < 0) & xu & (l_sl > 0)
        se = (cv < ema200) & (iv > 0) & (sv > 0) & xd & (s_sl > 0)
    rr = float(p["rr"])
    sl = np.where(le, l_sl, np.where(se, s_sl, np.nan))
    return le, se, sl, sl * rr


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, _, _ = _setup(bars_df, p)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, _, sl, tp = _setup(bars_df, p)
    ix = bars_df.index
    return {"sl_stop": pd.Series(sl, index=ix).shift(1), "tp_stop": pd.Series(tp, index=ix).shift(1)}


def portfolio_kwargs(**params):
    return {}
