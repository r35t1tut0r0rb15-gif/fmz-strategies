"""Liquidity sweeps with an RSI divergence in the SMA 50 trend and a 1.5 ATR stop / 3 ATR target, broker days: a bar
making the 5-bar low but closing above the previous low, with RSI 14 above its own 5-bar low, above the SMA 50 goes
long; the mirror below the SMA 50 goes short.
Port of FMZ strategy #488156 "流动性捕捉与智能资金分歧指标结合策略-Liquidity-Grab-Smart-Money-Divergence-Indicator-Combination-Strategy" (Liquidity Grab + Smart Money Divergence Strategy).

FMZ source id: 488156

Source
    https://www.fmz.com/strategy/488156 (PineScript v5, FMZ last modified 2025-03-25 15:12:43).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 180-217), RSI 14, lookback 5, SMA 50, ATR 14 x 1.5
    sweepLow = lowest(low, 5) == low and close > low[1];  bullishDivergence = sweepLow and rsi > lowest(rsi, 5)
    buy = bullishDivergence and close > sma50 -> entry + exit(stop = close - 1.5 ATR, limit = close + 3 ATR)
    sell mirrored with highest / high[1] and close < sma50

Interpretation choices (Pine rules in SURVEY_README.md)
    * The windows include the current bar, as written. The bracket is fixed at the signal bar: sl_stop = atr_mult x
      ATR / close, tp_stop = 2 x that, shifted one bar inside stops() and re-based on the fill (house rule).
    * A same-side signal while held re-places the bracket from the new bar: mark trailing_stop_pending; the port keeps
      the entry's bracket.
    * Entries reverse (REVERSAL INTENDED); the two signals need opposite trend sides. Stop module: portfolio_kwargs
      {} (D4). Daily bars are broker days (17:00 America/New_York), stamped with their first minute; FREQ = "1D"
      from the backtest header: coarse_bar_stop.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket from the signal bar (re-placement marked).
    2 generic: PASS, rolling extremes, an oscillator, a moving average and ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 1 % of equity quoted; the bracket ported via stops() and quoted in original_sizing.txt.
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

NAME = "fmz_488156_sweep_rsi_divergence_bracket"
FAMILY = "liquidity_sweep"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "lookback": [5, 10],
    "atr_mult": [1.5, 2.5],
}
DEFAULT_PARAMS = {"rsi_len": 14, "lookback": 5, "ma_len": 50, "atr_len": 14, "atr_mult": 1.5}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["lookback"])
    rsi = _rsi(c, int(p["rsi_len"]))
    ma = c.rolling(int(p["ma_len"])).mean()
    sweep_lo = (lo.rolling(n).min() == lo) & (c > lo.shift(1))
    sweep_hi = (h.rolling(n).max() == h) & (c < h.shift(1))
    long_e = (sweep_lo & (rsi > rsi.rolling(n).min()) & (c > ma)).astype(bool)
    short_e = (sweep_hi & (rsi < rsi.rolling(n).max()) & (c < ma)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    sl = (p["atr_mult"] * _atr(bars_df, int(p["atr_len"])) / bars_df["close"]).shift(1)
    return {"sl_stop": sl, "tp_stop": 2 * sl}


def portfolio_kwargs(**params):
    return {}
