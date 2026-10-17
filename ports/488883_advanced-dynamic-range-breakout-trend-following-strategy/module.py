"""Keltner (EMA 20, 2 ATR) breakouts in the EMA 200 trend with an RSI filter, an ATR bracket and an EMA 20 close exit,
broker days: the close crossing above the upper band with the close above EMA 200 and RSI 14 above 50 goes long; the
mirror goes short; each trade has a 1.5 ATR stop and a 2 ATR target, and the close crossing back through EMA 20
closes it.
Port of FMZ strategy #488883 "高级动态范围突破趋势追踪策略-Advanced-Dynamic-Range-Breakout-Trend-Following-Strategy" (Enhanced Keltner Channel Strategy).

FMZ source id: 488883

Source
    https://www.fmz.com/strategy/488883 (PineScript v5, FMZ last modified 2025-03-31 15:43:43).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 194-239), EMA 20 / ATR 20 x 2, EMA 200, RSI 14, bracket 1.5 / 2 x ATR(14)
    long = crossover(close, upper) and close > ema200 and rsi > 50;  short = crossunder(close, lower) and close < ema200 and rsi < 50
    entry + exit(stop = close -+ 1.5 ATR14, limit = close +- 2 ATR14);  crossunder(close, ema20) -> close long; crossover -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is placed once, on the signal bar: sl_stop = 1.5 x ATR(14) / close, tp_stop = 2 x ATR(14) / close,
      shifted one bar inside stops(), re-based on the fill (house rule).
    * Every signal bar is an entry (raw signals; the engine ignores a same-side entry while held). The EMA 20 crosses
      are close-based exits (an exit cannot fall on its own side's entry bar). Entries reverse (REVERSAL INTENDED).
    * Stop module: portfolio_kwargs {} (D4). Daily bars are broker days (17:00 America/New_York), stamped with their
      first minute; FREQ = "1D" from the backtest header: coarse_bar_stop.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at the signal bar.
    2 generic: PASS, ATR bands, EMAs, RSI and ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code; the bracket ported via stops() and quoted in original_sizing.txt.
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

NAME = "fmz_488883_keltner_breakout_trend_atr_bracket"
FAMILY = "volatility_channel_breakout"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "mult": [2.0, 1.5],
    "sl_atr": [1.5, 3.0],
}
DEFAULT_PARAMS = {"length": 20, "mult": 2.0, "trend": 200, "rsi_len": 14, "sl_atr": 1.5, "tp_atr": 2.0}


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
    n = int(p["length"])
    ema = c.ewm(span=n, adjust=False).mean()
    atr = _atr(bars_df, n)
    up_b, lo_b = ema + p["mult"] * atr, ema - p["mult"] * atr
    et = c.ewm(span=int(p["trend"]), adjust=False).mean()
    rsi = _rsi(c, int(p["rsi_len"]))
    long_e = ((c > up_b) & (c.shift(1) <= up_b.shift(1)) & (c > et) & (rsi > 50)).astype(bool)
    short_e = ((c < lo_b) & (c.shift(1) >= lo_b.shift(1)) & (c < et) & (rsi < 50)).astype(bool)
    long_x = ((c < ema) & (c.shift(1) >= ema.shift(1)) & ~short_e).astype(bool)
    short_x = ((c > ema) & (c.shift(1) <= ema.shift(1)) & ~long_e).astype(bool)
    return long_e, long_x, short_e, short_x


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    frac = _atr(bars_df, 14) / bars_df["close"]
    return {"sl_stop": (p["sl_atr"] * frac).shift(1), "tp_stop": (p["tp_atr"] * frac).shift(1)}


def portfolio_kwargs(**params):
    return {}
