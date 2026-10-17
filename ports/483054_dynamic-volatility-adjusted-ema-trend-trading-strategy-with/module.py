"""EMA 9 / 21 crosses with RSI off its extreme and the close more than 1.5 ATR beyond EMA 9, with reversals, the
opposite cross and a 1 % close-based stop as exits, 1-minute bars.
Port of FMZ strategy #483054 "动态波动率跟踪均线趋势交易策略与智能止损系统-Dynamic-Volatility-Adjusted-EMA-Trend-Trading-Strategy-with-Smart-Stop-Loss-System" (Enhanced Scalping Strategy with Stop Loss).

FMZ source id: 483054

Source
    https://www.fmz.com/strategy/483054 (PineScript v6, FMZ last modified 2025-02-21 11:11:26).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 117-189), EMA 9 / 21 (on a 1-minute chart), RSI 14 (70 / 30), ATR 14 x 1.5,
stop 1 %
    long = crossover(ema9, ema21) and rsi < 70 and close > ema9 + 1.5 ATR: close short, entry long, stop level =
    close x 0.99; short mirrored
    exit long = in long and (crossunder(ema9, ema21) or close <= stop level) -> close (short mirrored)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The lengths switch with the chart timeframe (1 minute: 9 / 21 / 14); the backtest header is 1 minute, so those
      are the lengths. FREQ = "1min".
    * The 1 % stop is checked on bar closes and acts through strategy.close: an exit signal at the next open (rule 3;
      as #489638), not a broker stop. No stop module.
    * close + entry is a reversal (REVERSAL INTENDED). The exits act on the trade flag, never on the entry's own bar
      (they cannot be true there). Target-position state machine, exits only on going flat.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the close-based stop is an exit signal.
    2 generic: PASS, moving averages, RSI, ATR multiples and a percentage stop.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing in the source (strategy() defaults).
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_483054_ema9_21_atr_extension_close_stop"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "atr_mult": [1.5, 1.0],
    "stop_pct": [1.0, 2.0],
}
DEFAULT_PARAMS = {"fast": 9, "slow": 21, "rsi_len": 14, "rsi_ob": 70, "rsi_os": 30, "atr_len": 14,
                  "atr_mult": 1.5, "stop_pct": 1.0}


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


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow"]), adjust=False).mean()
    rsi = _rsi(c, int(p["rsi_len"]))
    band = p["atr_mult"] * _atr(bars_df, int(p["atr_len"]))
    x_up = ((f > s) & (f.shift(1) <= s.shift(1))).to_numpy()
    x_dn = ((f < s) & (f.shift(1) >= s.shift(1))).to_numpy()
    long_c = x_up & (rsi < p["rsi_ob"]).to_numpy() & (c > f + band).to_numpy()
    short_c = x_dn & (rsi > p["rsi_os"]).to_numpy() & (c < f - band).to_numpy()
    cv = c.to_numpy(dtype=float)
    k = p["stop_pct"] / 100
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    pos, stop = 0, np.nan
    for i in range(m):
        if long_c[i]:
            pos, stop = 1, cv[i] * (1 - k)
        if short_c[i]:
            pos, stop = -1, cv[i] * (1 + k)
        if pos == 1 and (x_dn[i] or cv[i] <= stop):
            pos = 0
        if pos == -1 and (x_up[i] or cv[i] >= stop):
            pos = 0
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
