"""SMA 9 / 21 crosses with RSI 14 not at an extreme and a 0.5 % stop / 2 R target from the entry, 1-hour bars: SMA 9
crossing above SMA 21 with RSI below 70 goes long; crossing below with RSI above 30 goes short.
Port of FMZ strategy #483082 "基于动态波动率调整的双均线交叉与RSI-ATR复合过滤交易系统-Dynamic-Volatility-Adjusted-Dual-Moving-Average-Crossover-System-with-RSI-ATR-Composite-Filter" (Simplified MA Crossover Strategy with Disable Options).

FMZ source id: 483082

Source
    https://www.fmz.com/strategy/483082 (PineScript v5, FMZ last modified 2025-02-21 11:58:43).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 98-149), SMA 9 / 21, RSI 14 (70 / 30) on, ATR 14 > 0.005 on, SL 0.5 %, RR 2
    long = crossover(sma9, sma21) and rsi < 70 and atr > 0.005; short = crossunder and rsi > 30 and atr > 0.005
    entry + exit(limit = avg_price x (1 +- 1 %), stop = avg_price x (1 -+ 0.5 %)) on signal bars

Interpretation choices (Pine rules in SURVEY_README.md)
    * The ATR filter compares ATR with 0.005 price units: always true on the author's market (Binance SOL_USDT, 1-hour
      ATR about 1.8 USD), so it is dropped as inert (as #492009).
    * The exit is issued on signal bars from strategy.position_avg_price, na while flat (the opposite trade's price
      while reversing): the port applies the 0.5 % / 1 % bracket from the fill (the evident intent), as #489289.
      Decision owed: keep this, or port the literal behaviour.
    * The risk-based qty is sizing: not ported. Entries reverse (REVERSAL INTENDED). Stop module: portfolio_kwargs {}
      (D4). FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket from the fill (decision owed).
    2 generic: PASS, moving averages, RSI and percentage distances (the price-unit ATR floor is inert).
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the risk-based qty is quoted in original_sizing.txt and not ported; the bracket via stops().
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

NAME = "fmz_483082_sma9_21_cross_rsi_pct_bracket_rr"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_pct": [0.5, 1.0],
    "rr": [2.0, 3.0],
}
DEFAULT_PARAMS = {"fast": 9, "slow": 21, "rsi_len": 14, "rsi_ob": 70, "rsi_os": 30, "sl_pct": 0.5, "rr": 2.0}


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
    f, s = c.rolling(int(p["fast"])).mean(), c.rolling(int(p["slow"])).mean()
    rsi = _rsi(c, int(p["rsi_len"]))
    long_e = ((f > s) & (f.shift(1) <= s.shift(1)) & (rsi < p["rsi_ob"])).astype(bool)
    short_e = ((f < s) & (f.shift(1) >= s.shift(1)) & (rsi > p["rsi_os"])).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    sl = p["sl_pct"] / 100
    return {"sl_stop": sl, "tp_stop": p["rr"] * sl}


def portfolio_kwargs(**params):
    return {}
