"""Any-of momentum signals, 1-hour bars: the SMA 50 crossing over the close, a MACD signal cross up, an RSI capitulation, a Bollinger reclaim, or the EMA 50 at or above the EMA 100 goes long; else the
mirrored set goes short; reversing.
Port of FMZ strategy #442349 "Momentum Indicator Aggregation Trading Strategy" (Kesin Etkili Analiz V1 - Artun Sinan).

FMZ source id: 442349

Source
    https://www.fmz.com/strategy/442349 (PineScript v5, FMZ last modified 2024-02-21 11:59:22).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 175-293), EMA 50 / 100; SMA 50; MACD 12 / 26 / 9; RSI 14 (70 / 30); BB 20 / 2; backtest year 2019 (yearin >= year); fib levels plotted only
    buy = crossover(ma, close) or crossover(macd, signal) or (rsi < 30 and crossunder(rsi, 50)) or (close > upper and crossover(close, middle)) or (ema50 >= ema100 and 2019 >= year)
    sell = crossunder(ma, close) or crossunder(macd, signal) or (rsi > 70 and crossover(rsi, 50)) or (close < lower and crossunder(close, middle)) or (ema100 < ema50 and 2019 >= year);  buy -> entry Long, else sell -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * "yearin >= year" is the author's date bound (the input is labelled a start year), dropped like other
      date windows, so the EMA terms always apply: in an uptrend (EMA 50 at or above the EMA 100) the long
      term holds every bar, and both EMA terms test the same side, as written (the long is checked first).
      and binds tighter than or. The fib levels and exitSignal are only plotted. strategy.entry reverses:
      REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, any-of momentum signals.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_442349_any_of_momentum_signals_reversal"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_short": [50, 20],
    "ema_long": [100, 200],
}
DEFAULT_PARAMS = {"ema_short": 50, "ema_long": 100, "ma_period": 50, "fast": 12, "slow": 26, "signal": 9,
                  "rsi_period": 14, "rsi_ob": 70, "rsi_os": 30, "bb_period": 20, "bb_std": 2.0}


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
    up = _rma(d.clip(lower=0), n)
    dn = _rma((-d).clip(lower=0), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100.0 - 100.0 / (1.0 + up / dn)
    r = r.where(up != 0, 0.0).where(dn != 0, 100.0)    # Pine: down == 0 -> 100, else up == 0 -> 0
    return r.where(up.notna() & dn.notna())


def _xo(a, b):
    return (a > b) & (a.shift(1) <= b.shift(1))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    e1 = c.ewm(span=int(p["ema_short"]), adjust=False).mean()
    e2 = c.ewm(span=int(p["ema_long"]), adjust=False).mean()
    ma = c.rolling(int(p["ma_period"])).mean()
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    sig = macd.ewm(span=int(p["signal"]), adjust=False).mean()
    r = _rsi(c, int(p["rsi_period"]))
    n = int(p["bb_period"])
    mid = c.rolling(n).mean()
    dev = float(p["bb_std"]) * c.rolling(n).std(ddof=0)
    upper, lower = mid + dev, mid - dev
    fifty = pd.Series(50.0, index=c.index)
    buy = (_xo(ma, c) | _xo(macd, sig) | ((r < float(p["rsi_os"])) & _xo(fifty, r))
           | ((c > upper) & _xo(c, mid)) | (e1 >= e2))
    sell = (_xo(c, ma) | _xo(sig, macd) | ((r > float(p["rsi_ob"])) & _xo(r, fifty))
            | ((c < lower) & _xo(mid, c)) | (e2 < e1))
    false = pd.Series(False, index=c.index)
    return buy, false, sell & ~buy, false.copy()


def portfolio_kwargs(**params):
    return {}
