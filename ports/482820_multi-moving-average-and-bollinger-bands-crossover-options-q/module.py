"""SMA 5 / 11 crosses on the SMA 55 side with the close outside the opposite Bollinger band (22, 1.5), closed by a close
crossing the SMA 5 or the SMA 55, with a 1.5 ATR stop and a 3 ATR target, five-minute bars.
Port of FMZ strategy #482820 "多重移动平均线与布林带交叉期权量化交易策略-Multi-Moving-Average-and-Bollinger-Bands-Crossover-Options-Quantitative-Trading-Strategy" (MA5 MA11 Bollinger Bands 22 Strategy).

FMZ source id: 482820

Source
    https://www.fmz.com/strategy/482820 (PineScript v5, FMZ last modified 2025-02-20 14:53:43).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 118-160), SMA 5 / 11 / 55, BB 22 / 1.5, ATR 14 (1.5 / 3)
    crossover(ma5, ma11) and close > ma55 and close < lowerBB -> entry long (short mirrored, close > upperBB)
    crossunder(close, ma5) or close < ma55 -> close long; crossover(close, ma5) or close > ma55 -> close short
    every bar: exit(stop = close -/+ 1.5 ATR, limit = close +/- 3 ATR) for the open side

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is re-issued every bar from the current close and ATR (a moving level): fixed at the entry as
      1.5 ATR / close and 3 ATR / close of the signal bar (shifted one bar inside stops(), re-based on the fill);
      mark trailing_stop_pending.
    * Closes are written after the entries: they act on the position held at the bar's start and never undo an
      entry on that bar (#430850). simulate() mirrors the house bracket from the fill so the closes see the position
      the engine holds (as #430254); exits are emitted only on going flat.
    * Entries reverse (REVERSAL INTENDED); the two sides cannot fall on one bar. Stop module: portfolio_kwargs {} (D4).
      FREQ = "5min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the moving bracket fixed at entry (marked).
    2 generic: PASS, three SMAs, Bollinger bands and ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: default quantity; the bracket via stops(), quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_482820_sma5_11_cross_bb_outside_sma55_atr_bracket"
FAMILY = "mean_reversion"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_mult": [1.5, 2.5],
    "tp_mult": [3.0, 5.0],
}
DEFAULT_PARAMS = {"fast": 5, "mid": 11, "trend": 55, "bb_len": 22, "bb_mult": 1.5, "atr_len": 14,
                  "sl_mult": 1.5, "tp_mult": 3.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


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
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]   # Pine's first true range is high - low
    return _rma(tr, n)


def _fracs(bars_df, p):
    a = (_atr(bars_df, int(p["atr_len"])) / bars_df["close"]).to_numpy()
    return p["sl_mult"] * a, p["tp_mult"] * a


def _run(bars_df, p):
    o, h, lo = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "low"))
    c = bars_df["close"]
    ma5, ma11, ma55 = (c.rolling(int(p[k])).mean() for k in ("fast", "mid", "trend"))
    n = int(p["bb_len"])
    basis = c.rolling(n).mean()
    dev = p["bb_mult"] * c.rolling(n).std(ddof=0)

    def xover(a, b):
        return (a > b) & (a.shift(1) <= b.shift(1))

    buy = (xover(ma5, ma11) & (c > ma55) & (c < basis - dev)).to_numpy()
    sell = (xover(ma11, ma5) & (c < ma55) & (c > basis + dev)).to_numpy()
    xl = (xover(ma5, c) | (c < ma55)).to_numpy()
    xs = (xover(c, ma5) | (c > ma55)).to_numpy()
    sl, tp = _fracs(bars_df, p)
    m = len(o)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos, entry_i, s_, t_ = 0, -1, 0.0, 0.0
    for i in range(m):
        if pos != 0 and 0 <= entry_i <= i:                 # house bracket from the fill price
            e = o[entry_i]
            if pos == 1 and (lo[i] <= e * (1 - s_) or h[i] >= e * (1 + t_)):
                pos = 0
            elif pos == -1 and (h[i] >= e * (1 + s_) or lo[i] <= e * (1 - t_)):
                pos = 0
        start = pos
        if buy[i] and pos != 1 and i + 1 < m and not np.isnan(sl[i]):
            le[i], pos, entry_i, s_, t_ = True, 1, i + 1, sl[i], tp[i]
        if sell[i] and pos != -1 and i + 1 < m and not np.isnan(sl[i]):
            se[i], pos, entry_i, s_, t_ = True, -1, i + 1, sl[i], tp[i]
        if xl[i] and start == 1 and pos == 1:
            lx[i], pos = True, 0
        if xs[i] and start == -1 and pos == -1:
            sx[i], pos = True, 0
    return le, lx, se, sx


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    idx = bars_df.index
    return tuple(pd.Series(a, index=idx) for a in _run(bars_df, p))


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    sl, tp = _fracs(bars_df, p)
    idx = bars_df.index
    return {"sl_stop": pd.Series(sl, index=idx).shift(1), "tp_stop": pd.Series(tp, index=idx).shift(1)}


def portfolio_kwargs(**params):
    return {}
