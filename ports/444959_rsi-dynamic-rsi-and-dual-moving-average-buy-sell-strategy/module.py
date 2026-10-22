"""RSI 2 extremes on the side of the SMA 200, 1-hour bars, with a fixed stop: RSI 2 at 20 or less above the SMA 200 goes long and RSI 2 at 80 or more closes it; RSI 2 at 80 or more under the SMA goes
short and a low under the EMA 20 with RSI 2 at 10 or less closes it; reversing; a 5000-tick stop on both sides.
Port of FMZ strategy #444959 "动态RSI双均线买卖策略Dynamic-RSI-and-Dual-Moving-Average-Buy-Sell-Strategy" (ag7 buy sell).

FMZ source id: 444959

Source
    https://www.fmz.com/strategy/444959 (PineScript v5, FMZ last modified 2024-03-15 14:36:30).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 145-176), RSI 2, levels 20 / 80 / 10; SMA 200; EMA 20 / 80 (as truth values); take profit 100000000 ticks, stop loss 5000 ticks, trailing 1000 ticks with offset 0 (na); 100 % of equity
    rsi2 <= 20 and close >= sma200 and ema20 -> entry Compra;  ema80 and rsi2 >= 80 -> close Compra;  exit(from Compra / Venda: profit = 1e8, loss = 5000, trail_points = 1000, trail_offset = na)
    rsi2 >= 80 and close <= sma200 and ema80 -> entry Venda;  low <= ema20 and rsi2 <= 10 -> close Venda

Interpretation choices (Pine rules in SURVEY_README.md)
    * The EMAs used as conditions are positive prices, so they are always true. Criterion 2: the
      5000-tick stop (mintick 0.1 = 500 price units) is re-expressed as sl_stop = k_atr x ATR(14) /
      close of the signal bar, shifted one bar inside stops() (re-based on the fill); 3.33 is the
      reading against a 1-hour BTC ATR near 150. The 1e8-tick target is out of reach and not ported;
      trail_points without trail_offset places no trailing stop (as before). A close called on the bar
      of the opposite entry leaves the reversal (house call-order rule). REVERSAL INTENDED. Stop module:
      portfolio_kwargs {} (driver D4). The 100 % of equity size is sizing. FREQ = "1h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; stop fixed at entry.
    2 generic: PASS, RSI 2 extremes with an SMA side filter; tick stop as an ATR multiple.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the 100 % of equity size stored; the tick inputs quoted in original_sizing.txt.
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

NAME = "fmz_444959_rsi2_extremes_sma200_side_atr_stop_reversal"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "k_atr": [3.33, 1.0],
    "sma_len": [200, 100],
}
DEFAULT_PARAMS = {"k_atr": 3.33, "sma_len": 200, "atr_len": 14, "ema_fast": 20}


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
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    return 100 - 100 / (1 + up / dn)


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    lo, c = bars_df["low"], bars_df["close"]
    r = _rsi(c, 2)
    sma = c.rolling(int(p["sma_len"])).mean()
    e20 = c.ewm(span=int(p["ema_fast"]), adjust=False).mean()
    le = (r <= 20) & (c >= sma)
    lx = r >= 80
    se = (r >= 80) & (c <= sma)
    sx = (lo <= e20) & (r <= 10)
    # a close called on the bar of the opposite entry leaves the reversal
    return le & ~se, lx & ~se, se, sx & ~le


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    f = float(p["k_atr"]) * _atr(bars_df, p["atr_len"]) / bars_df["close"]
    return {"sl_stop": f.shift(1)}


def portfolio_kwargs(**params):
    return {}
