"""Logistic EMA-gap and RSI "probabilities" with a cycling ATR bracket, broker days: when EMA 9 is above EMA 55 (by more
than a sliver) and RSI 14 is above about 52 the strategy goes long; the mirror goes short; each trade has a stop of
ATR / decay and a target 1.5 times that, where decay cycles with the bar count modulo 50.
Port of FMZ strategy #488008 "量子启发式概率趋势交易策略基于EMA和RSI的量化模型-Quantum-Inspired-Probability-Trend-Trading-Strategy-EMA-RSI-Based-Quantitative-Model" (Quantum-Inspired Trading Strategy).

FMZ source id: 488008

Source
    https://www.fmz.com/strategy/488008 (PineScript v6, FMZ last modified 2025-03-24 13:43:03).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 152-188), EMA 9 / 19 / 55, ATR 14, k 0.1
    trendProb = 1 / (1 + exp(-0.1 x (ema9 - ema55)));  bullish > 0.6, bearish < 0.4
    probabilityDirection = 1 / (1 + exp(-0.1 x (rsi - 50)));  long = > 0.55 and bullish;  short = < 0.45 and bearish
    decay = exp(-0.02 x (bar_index % 50));  stop = ATR / decay;  target = 1.5 ATR / decay
    entry + exit(stop = close -+ stop, limit = close +- target)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The RSI test is unit-free: > 0.55 means RSI > 50 + ln(0.55 / 0.45) / 0.1, about 52.0 (< 0.45: below about 48.0).
    * Criterion 2: the trend test reads a price difference: > 0.6 means ema9 - ema55 > ln(1.5) / 0.1, about 4.05 price
      units. On the author's daily BTC_USDT (daily ATR about 2000) that is about 0.002 ATR(14) (judgement before any
      backtest): trend_atr x ATR.
    * bar_index counts from the first bar of the data the module is given, as Pine counts from the chart's first bar.
    * The bracket is fixed at the signal bar (fractions of its close, shifted one bar inside stops(), re-based on the
      fill); a same-side signal while held re-places it: mark trailing_stop_pending; the port keeps the entry's.
    * Entries reverse (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (D4). Daily bars are broker days
      (17:00 America/New_York), stamped with their first minute; FREQ = "1D" from the backtest header:
      coarse_bar_stop.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket from the signal bar (re-placement marked).
    2 generic: ADAPT, the price-unit EMA gap -> an ATR multiple; RSI and ATR.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code; the bracket ported via stops() and quoted in original_sizing.txt.
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

NAME = "fmz_488008_logistic_ema_rsi_cycling_bracket"
FAMILY = "ma_trend_filter"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "trend_atr": [0.002, 0.25],
    "tp_mult": [1.5, 2.0],
}
DEFAULT_PARAMS = {"ema_short": 9, "ema_long": 55, "atr_len": 14, "k": 0.1, "trend_atr": 0.002, "tp_mult": 1.5,
                  "cycle": 50, "decay": 0.02}


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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]   # Pine's first true range is high - low
    return _rma(tr, n)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    gap = c.ewm(span=int(p["ema_short"]), adjust=False).mean() - c.ewm(span=int(p["ema_long"]), adjust=False).mean()
    thr = p["trend_atr"] * _atr(bars_df, int(p["atr_len"]))
    pdir = 1 / (1 + np.exp(-p["k"] * (_rsi(c, 14) - 50)))
    long_e = ((pdir > 0.55) & (gap > thr)).astype(bool)
    short_e = ((pdir < 0.45) & (gap < -thr)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    decay = np.exp(-p["decay"] * (np.arange(len(c)) % int(p["cycle"])))
    sl = (_atr(bars_df, int(p["atr_len"])) / decay / c).shift(1)
    return {"sl_stop": sl, "tp_stop": p["tp_mult"] * sl}


def portfolio_kwargs(**params):
    return {}
