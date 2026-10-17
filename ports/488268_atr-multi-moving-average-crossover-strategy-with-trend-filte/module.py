"""SMA 20 / EMA 89 crosses on the SMA 200 side, entries only from flat, with a 2 ATR stop and a 3 ATR target, 2-hour bars:
flat and above the SMA 200, the SMA 20 crossing above the EMA 89 goes long; flat and below it, the cross down goes
short; each trade leaves only on its bracket.
Port of FMZ strategy #488268 "趋势过滤多均线交叉ATR风控量化策略-Multi-Moving-Average-Crossover-Strategy-with-Trend-Filter-and-ATR-Risk-Management" (EMA Cross Strategy (20MA & 89EMA with 200MA Filter)).

FMZ source id: 488268

Source
    https://www.fmz.com/strategy/488268 (PineScript v5, FMZ last modified 2025-03-26 13:42:55).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 210-249), SMA 20, EMA 89, SMA 200, ATR 14, stop x 2, target x 3
    long = close > sma200 and position_size == 0 and crossover(sma20, ema89)
    short = close < sma200 and position_size == 0 and crossunder(sma20, ema89)
    entry + exit(stop = close -+ 2 ATR, limit = close +- 3 ATR), the ATR locked at the signal bar

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is fixed at the signal bar: sl_stop = sl_mult x ATR / close, tp_stop = tp_mult x ATR / close,
      shifted one bar inside stops() and re-based on the fill (house rule).
    * Entries only from flat: simulate() mirrors the house bracket from the fill bar (#430254), and an entry is allowed
      on the bar a stop or target is hit. Opposite entries cannot occur.
    * Stop module: portfolio_kwargs {} (D4). FREQ = "2h" from the backtest header: coarse_bar_stop.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at the signal bar.
    2 generic: PASS, moving averages and ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code; the bracket ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_488268_sma20_ema89_cross_flat_bracket"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_mult": [2.0, 1.5],
    "tp_mult": [3.0, 4.0],
}
DEFAULT_PARAMS = {"fast": 20, "slow": 89, "trend": 200, "atr_len": 14, "sl_mult": 2.0, "tp_mult": 3.0}


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
    a = _atr(bars_df, int(p["atr_len"])) / bars_df["close"]
    return p["sl_mult"] * a, p["tp_mult"] * a


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    f = c.rolling(int(p["fast"])).mean()
    s = c.ewm(span=int(p["slow"]), adjust=False).mean()
    t = c.rolling(int(p["trend"])).mean()
    go_l = ((c > t) & (f > s) & (f.shift(1) <= s.shift(1))).to_numpy()
    go_s = ((c < t) & (f < s) & (f.shift(1) >= s.shift(1))).to_numpy()
    sl_f, tp_f = (x.to_numpy(dtype=float) for x in _fracs(bars_df, p))
    ov, hv, lv = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "low"))
    m = len(c)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, fill_i, s_, t_ = 0, -1, np.nan, np.nan
    for i in range(m):
        if pos != 0 and i >= fill_i:                     # the house bracket from the fill price
            e = ov[fill_i]
            if pos == 1 and (lv[i] <= e * (1 - s_) or hv[i] >= e * (1 + t_)):
                pos = 0
            elif pos == -1 and (hv[i] >= e * (1 + s_) or lv[i] <= e * (1 - t_)):
                pos = 0
        if pos == 0 and go_l[i]:
            le[i], pos, fill_i, s_, t_ = True, 1, i + 1, sl_f[i], tp_f[i]
        elif pos == 0 and go_s[i]:
            se[i], pos, fill_i, s_, t_ = True, -1, i + 1, sl_f[i], tp_f[i]
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), false, pd.Series(se, index=idx), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    sl, tp = _fracs(bars_df, p)
    return {"sl_stop": sl.shift(1), "tp_stop": tp.shift(1)}


def portfolio_kwargs(**params):
    return {}
