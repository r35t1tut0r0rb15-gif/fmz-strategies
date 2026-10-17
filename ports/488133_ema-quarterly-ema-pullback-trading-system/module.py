"""EMA 10 / 21 reclaims with RSI below 40, long only, with a 15 % stop, 1-minute bars: the close crossing above EMA 10 or
EMA 21 while RSI 14 is below 40 goes long; the trade closes on a close 8 % above EMA 10 or a cross back below EMA 10,
and has a stop 15 % under the signal close.
Port of FMZ strategy #488133 "季度EMA动态回撤交易系统-Quarterly-EMA-Pullback-Trading-System" (Quarterly EMA Strategy).

FMZ source id: 488133

Source
    https://www.fmz.com/strategy/488133 (PineScript v5, FMZ last modified 2025-03-25 13:15:22).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 295-330), EMA 10 / 21, RSI 14 < 40, exit +8 % over EMA 10, stop 15 %
    enterLong = (crossover(close, ema10) or crossover(close, ema21)) and rsi < 40 -> entryPrice = close, entry long
    close > ema10 x 1.08 or crossunder(close, ema10) -> close long
    entryPrice set: exit(stop = entryPrice x 0.85) every bar

Interpretation choices (Pine rules in SURVEY_README.md)
    * The close acts on the position held at the bar's start and never undoes an entry on that bar (#430850).
    * The stop is 15 % under the signal close, re-based on the fill: sl_stop 0.15 (scalar). A later signal while held
      moves entryPrice and so the stop: mark trailing_stop_pending; the port keeps the entry's stop. simulate()
      mirrors the stop from the fill bar (#430254) so entries follow the position the engine holds.
    * Long only: opposite entries cannot occur. Stop module: portfolio_kwargs {} (D4). FREQ = "1min" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; stop fixed at the signal bar (moves marked).
    2 generic: PASS, EMAs, an oscillator and percentages.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity quoted; the stop ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_488133_ema_reclaim_rsi40_long"
FAMILY = "ma_pullback"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "rsi_max": [40, 50],
    "sl_pct": [15.0, 5.0],
}
DEFAULT_PARAMS = {"rsi_len": 14, "rsi_max": 40, "jump_pct": 8.0, "sl_pct": 15.0}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    e10, e21 = c.ewm(span=10, adjust=False).mean(), c.ewm(span=21, adjust=False).mean()
    rsi = _rsi(c, int(p["rsi_len"]))
    x10 = (c > e10) & (c.shift(1) <= e10.shift(1))
    x21 = (c > e21) & (c.shift(1) <= e21.shift(1))
    go = ((x10 | x21) & (rsi < p["rsi_max"])).to_numpy()
    out = ((c > e10 * (1 + p["jump_pct"] / 100)) | ((c < e10) & (c.shift(1) >= e10.shift(1)))).to_numpy()
    s_ = p["sl_pct"] / 100
    ov, lv = bars_df["open"].to_numpy(dtype=float), bars_df["low"].to_numpy(dtype=float)
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, fill_i = 0, -1
    for i in range(m):
        if pos == 1 and i >= fill_i and lv[i] <= ov[fill_i] * (1 - s_):   # the house stop from the fill price
            pos = 0
        start = pos
        if go[i] and pos == 0:
            pos, fill_i = 1, i + 1
        if out[i] and start == 1:
            pos = 0
        le[i] = start == 0 and pos == 1
        lx[i] = start == 1 and pos == 0
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), pd.Series(lx, index=idx), false, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": p["sl_pct"] / 100}


def portfolio_kwargs(**params):
    return {}
