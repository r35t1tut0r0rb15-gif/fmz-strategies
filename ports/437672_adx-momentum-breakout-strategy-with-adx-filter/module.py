"""Upper Bollinger band re-entries with an ADX filter, 5-minute bars, long only as written: the close crossing back under the upper band (SMA 33 + 2 sigma) while the fast ADX EMA (8) is under the slow one (15)
buys, despite the entry's name; each trade has a tick bracket (target 800, stop 400) re-expressed as ATR multiples.
Port of FMZ strategy #437672 "顺势突破ADX过滤交易策略Momentum-Breakout-Strategy-with-ADX-Filter" (Hizbullah XAUUSD Sniper).

FMZ source id: 437672

Source
    https://www.fmz.com/strategy/437672 (PineScript v4, FMZ last modified 2024-01-04 17:12:30).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 132-160), BB 33 x 2, ADX 4 (SMA smoothing), ADX EMAs 8 / 15, take profit 800 / stop 400 ticks
    Condition1 = crossunder(close, upper) and ema(DX, 8) < ema(DX, 15) -> strategy.entry("ShortEntry", true) (a LONG entry);  exit(profit = 800, loss = 400)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The entry named "ShortEntry" passes direction true, a long, as written (an intended short version is
      owed). The ADX is the script's own (SMA-smoothed DM and true range over 4 bars). Criterion 2: the
      ticks are re-expressed as sl_stop = k_atr x ATR(14) / close and tp_stop = 2 x sl_stop of the signal
      bar, shifted one bar inside stops() and re-based on the fill; 0.67 is the reading (400 ticks of 0.1
      on BTC against a 5-minute ATR near 60), 1.5 a wider stop. The XAUUSD title names an instrument; the
      rules are generic. Long only. Stop module: portfolio_kwargs {} (driver D4). No sizing code. FREQ =
      "5min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: ADAPT, tick bracket -> ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the tick inputs stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_437672_upper_band_reentry_adx_long"
FAMILY = "bollinger_breakout"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "length": [33, 20],
    "k_atr": [0.67, 1.5],
}
DEFAULT_PARAMS = {"length": 33, "k_atr": 0.67, "mult": 2.0, "adx_len": 4, "adx_fast": 8, "adx_slow": 15,
                  "atr_len": 14, "tp_ratio": 2.0}


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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    basis = c.rolling(n).mean()
    upper = basis + float(p["mult"]) * c.rolling(n).std(ddof=0)
    c1 = c.shift(1).fillna(0.0)
    h1, l1 = h.shift(1).fillna(0.0), lo.shift(1).fillna(0.0)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    k = int(p["adx_len"])
    str_ = tr.rolling(k).mean()
    dmp = pd.Series(np.where(h - h1 > l1 - lo, np.maximum(h - h1, 0), 0.0), index=c.index)
    dmm = pd.Series(np.where(l1 - lo > h - h1, np.maximum(l1 - lo, 0), 0.0), index=c.index)
    with np.errstate(divide="ignore", invalid="ignore"):
        dip = dmp.rolling(k).mean() / str_ * 100
        dim = dmm.rolling(k).mean() / str_ * 100
        dx = (dip - dim).abs() / (dip + dim) * 100
    a1 = dx.ewm(span=int(p["adx_fast"]), adjust=False).mean()
    a2 = dx.ewm(span=int(p["adx_slow"]), adjust=False).mean()
    cond = (c < upper) & (c.shift(1) >= upper.shift(1)) & (a1 < a2)
    false = pd.Series(False, index=bars_df.index)
    return cond, false, false.copy(), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    f = float(p["k_atr"]) * _atr(bars_df, p["atr_len"]) / bars_df["close"]
    return {"sl_stop": f.shift(1), "tp_stop": (float(p["tp_ratio"]) * f).shift(1)}


def portfolio_kwargs(**params):
    return {}
