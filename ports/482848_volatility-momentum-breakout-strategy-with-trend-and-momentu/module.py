"""Closes beyond the prior 20-bar high (low) by 1.5 ATR on the EMA 50 and RSI 50 side, with a 1 ATR stop and a 2 R
target from the entry, 10-minute bars.
Port of FMZ strategy #482848 "波动率动量突破交易策略结合趋势和动量过滤-Volatility-Momentum-Breakout-Strategy-with-Trend-and-Momentum-Filters" (Volatility Momentum Breakout Strategy).

FMZ source id: 482848

Source
    https://www.fmz.com/strategy/482848 (PineScript v5, FMZ last modified 2025-02-20 15:13:31).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 133-200), ATR 14, breakout 1.5 ATR over 20 bars, EMA 50, RSI 14 (50 / 50),
stop 1 ATR, RR 2
    long = close > highest(high[1], 20) + 1.5 ATR and close > ema50 and rsi > 50 (short mirrored)
    while held: exit(stop = entry - 1 ATR, limit = entry + 2 (entry - stop)) on every bar, entry = the fill price

Interpretation choices (Pine rules in SURVEY_README.md)
    * The exits are re-issued every bar from the fill with the CURRENT ATR (a moving level): fixed at the entry as
      1 ATR / close of the signal bar and rr x that (shifted one bar inside stops(), re-based on the fill); mark
      trailing_stop_pending.
    * Every bar in the condition is an entry signal (same-side ignored while held). Entries reverse (REVERSAL
      INTENDED). Stop module: portfolio_kwargs {} (D4). FREQ = "10min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the moving bracket fixed at entry (marked).
    2 generic: PASS, rolling extremes, an EMA, RSI and ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 5 % of equity and the risk input quoted; the bracket via stops(), quoted in original_sizing.txt.
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

NAME = "fmz_482848_atr_breakout_ema_rsi_atr_rr"
FAMILY = "breakout"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "10min"  # backtest header period: 10m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "atr_mult": [1.5, 1.0],
    "rr": [2.0, 3.0],
}
DEFAULT_PARAMS = {"atr_len": 14, "atr_mult": 1.5, "lookback": 20, "ema_len": 50, "rsi_len": 14,
                  "stop_mult": 1.0, "rr": 2.0}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    atr = _atr(bars_df, int(p["atr_len"]))
    n = int(p["lookback"])
    up = h.shift(1).rolling(n).max() + p["atr_mult"] * atr
    dn = lo.shift(1).rolling(n).min() - p["atr_mult"] * atr
    ema = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    rsi = _rsi(c, int(p["rsi_len"]))
    long_e = ((c > up) & (c > ema) & (rsi > 50)).astype(bool)
    short_e = ((c < dn) & (c < ema) & (rsi < 50)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    sl = (p["stop_mult"] * _atr(bars_df, int(p["atr_len"])) / bars_df["close"]).shift(1)
    return {"sl_stop": sl, "tp_stop": p["rr"] * sl}


def portfolio_kwargs(**params):
    return {}
