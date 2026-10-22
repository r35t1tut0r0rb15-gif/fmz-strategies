"""Averaged four-MACD histogram turning green and rising on a rising linear-regression candle with the RSI 14 under 55, 1-hour bars, long only, with a 4 % take-profit from the fill.
Port of FMZ strategy #445833 "TrippleMACD均线交叉与相对强弱指标结合的高频加密货币交易策略High-Frequency-Cryptocurrency-Trading-Strategy-Combining-TrippleMACD-Crossover-and-Relative-Strength-Index" (TrippleMACD + RSI strategy).

FMZ source id: 445833

Source
    https://www.fmz.com/strategy/445833 (PineScript v5, FMZ last modified 2024-03-22 15:41:46).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 149-363), MACD pairs 5 / 8, 13 / 21, 34 / 144 (the fourth repeats 34 / 144), signal 9; linreg candles 11; RSI 14 (rma form), level 55; take profit avg x 1.04
    hist = mean(macd1..4) - mean(signal1..4);  green = hist >= 0 ? (rising ? "G" : "GL") : (rising ? "RL" : "R")
    Buy = green == "G" and green[1] not "G" / "GL" and linreg open < linreg close and rsi < 55 -> entry long;  exit(long, limit = avg x 1.04)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The fourth MACD reads the third pair's lengths (34 / 144), as written; the "SMA2" / "SMA3"
      options never match, so all averages are EMAs; all four signals use length 9. The take-profit is
      sent every bar from the average price (na while flat), so it is a fixed 4 % of the fill:
      tp_stop 0.04 (as #440797). StopBuy only raises an alert, the divergence block is off, and the
      RSI moving average only plots. A repeated Buy while long is ignored (one position). Long only.
      Stop module: portfolio_kwargs {} (driver D4). No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; target fixed from the fill.
    2 generic: PASS, MACD histogram colour change with linreg candle and RSI filters, fixed target.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_445833_triple_macd_green_turn_linreg_rsi_tp_long"
FAMILY = "macd_momentum"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "tp": [0.04, 0.02],
    "rsi_max": [55.0, 45.0],
}
DEFAULT_PARAMS = {"tp": 0.04, "rsi_max": 55.0, "signal": 9, "linreg_len": 11, "rsi_len": 14}


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


def _linreg(y, n):
    """Pine's linreg(y, n, 0): the least-squares line over the last n bars, read at the newest bar."""
    k = pd.Series(np.arange(len(y), dtype=float), index=y.index)
    sy = y.rolling(n).sum()
    sky = (k * y).rolling(n).sum()
    x0 = k - (n - 1)                                   # x = k - x0 runs 0 .. n-1 inside the window
    sxy = sky - x0 * sy
    sx = n * (n - 1) / 2.0
    sxx = (n - 1) * n * (2 * n - 1) / 6.0
    slope = (n * sxy - sx * sy) / (n * sxx - sx * sx)
    icpt = (sy - slope * sx) / n
    return icpt + slope * (n - 1)


def _ema(x, n):
    return x.ewm(span=int(n), adjust=False).mean()


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, c = bars_df["open"], bars_df["close"]
    pairs = ((5, 8), (13, 21), (34, 144), (34, 144))     # the fourth repeats the third, as written
    macds = [_ema(c, f) - _ema(c, s) for f, s in pairs]
    sigs = [_ema(mc, int(p["signal"])) for mc in macds]
    hist = (sum(macds) / 4 - sum(sigs) / 4).to_numpy()
    m = len(hist)
    g = np.full(m, "", dtype=object)
    for i in range(m):
        rising = i > 0 and hist[i - 1] < hist[i]
        if np.isnan(hist[i]):
            g[i] = "R"
        elif hist[i] >= 0:
            g[i] = "G" if rising else "GL"
        else:
            g[i] = "RL" if rising else "R"
    g1 = np.concatenate(([""], g[:-1]))
    n = int(p["linreg_len"])
    bo, bc = _linreg(o, n).to_numpy(), _linreg(c, n).to_numpy()
    d = c.diff()
    ln = int(p["rsi_len"])
    up, dn = _rma(d.clip(lower=0), ln), _rma((-d).clip(lower=0), ln)
    with np.errstate(divide="ignore", invalid="ignore"):
        base = 100 - 100 / (1 + up / dn)
    rsi = np.where(dn == 0, 100.0, np.where(up == 0, 0.0, base))
    with np.errstate(invalid="ignore"):
        buy = (g == "G") & (g1 != "G") & (g1 != "GL") & (bo < bc) & (rsi < float(p["rsi_max"]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(buy.astype(bool), index=ix), false, false.copy(), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"tp_stop": float(p["tp"])}


def portfolio_kwargs(**params):
    return {}
