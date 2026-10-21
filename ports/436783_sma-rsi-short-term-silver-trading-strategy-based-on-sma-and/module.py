"""SMA 10 / 30 crossings with an RSI side filter and an ATR bracket, 1-hour bars: a crossing up with the RSI 14 above 50 goes long with a stop 3 ATR under the signal bar's low and a target 3 ATR over its high;
a crossing down with the RSI under 50 goes short with a stop 2 ATR over the high and a target 2 ATR under the low; reversing.
Port of FMZ strategy #436783 "基于SMA均线和RSI指标的白银价格短期交易策略Short-Term-Silver-Trading-Strategy-Based-on-SMA-and-RSI-Indicators" (SMA 10 30 ATR RSI).

FMZ source id: 436783

Source
    https://www.fmz.com/strategy/436783 (PineScript v5, FMZ last modified 2023-12-27 16:42:05).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 112-132), SMA 10 / 30, RSI 14, ATR 14; long bracket 3 ATR, short bracket 2 ATR
    longCondition = crossover(sma 10, sma 30):  entry long (qty 1, when rsi > 50), exit(stop = low - 3 atr, limit = high + 3 atr)
    shortCondition = crossunder(...):  entry short (qty 1, when rsi < 50), exit(stop = high + 2 atr, limit = low - 2 atr)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket levels are the signal bar's (low / high +- k ATR), re-expressed as distances from the
      signal close (sl_stop / tp_stop fractions), shifted one bar inside stops() and re-based on the fill.
      The script also re-sends its exit on a crossing whose RSI filter blocks the entry, which re-arms an
      open trade's bracket at the new bar's levels; that re-arming is not ported (the bracket stays at the
      entry's levels). REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). The fixed size 1 is
      sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: PASS, ATR bracket around the signal bar.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the fixed quantity stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG436783 (2 members, best partner #442232, Jaccard 0.806); ND430053 (2 members, best partner #430053, Jaccard 0.777); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_436783_sma_cross_rsi_atr_bracket"
FAMILY = "ma_cross"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "fast": [10, 20],
    "slow": [30, 60],
}
DEFAULT_PARAMS = {"fast": 10, "slow": 30, "rsi_len": 14, "atr_len": 14, "k_long": 3.0, "k_short": 2.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
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
    up = _rma(d.clip(lower=0), n)
    dn = _rma((-d).clip(lower=0), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100.0 - 100.0 / (1.0 + up / dn)
    r = r.where(up != 0, 0.0).where(dn != 0, 100.0)    # Pine: down == 0 -> 100, else up == 0 -> 0
    return r.where(up.notna() & dn.notna())


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def _setup(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    f = c.rolling(int(p["fast"])).mean()
    s = c.rolling(int(p["slow"])).mean()
    r = _rsi(c, int(p["rsi_len"]))
    le = (f > s) & (f.shift(1) <= s.shift(1)) & (r > 50)
    se = (f < s) & (f.shift(1) >= s.shift(1)) & (r < 50)
    atr = _atr(bars_df, p["atr_len"])
    kl, ks = float(p["k_long"]), float(p["k_short"])
    sl = pd.Series(np.where(le, (c - (lo - kl * atr)) / c, np.where(se, (h + ks * atr - c) / c, np.nan)),
                   index=c.index)
    tp = pd.Series(np.where(le, (h + kl * atr - c) / c, np.where(se, (c - (lo - ks * atr)) / c, np.nan)),
                   index=c.index)
    return le, se, sl, tp


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, _, _ = _setup(bars_df, p)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, _, sl, tp = _setup(bars_df, p)
    return {"sl_stop": sl.shift(1), "tp_stop": tp.shift(1)}


def portfolio_kwargs(**params):
    return {}
