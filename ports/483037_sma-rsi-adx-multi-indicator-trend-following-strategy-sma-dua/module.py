"""SMA 10 / 200 crosses confirmed by RSI 14 and ADX 14, with a tick trailing stop as a tight ATR trail, 4-minute
bars: SMA 10 crossing above SMA 200 with RSI above 50 and ADX above 20 goes long; the mirror goes short.
Port of FMZ strategy #483037 "多重指标趋势跟踪策略基于SMA双线交叉结合RSI和ADX的动态波动率优化系统-Multi-Indicator-Trend-Following-Strategy-SMA-Dual-Line-Crossover-with-RSI-and-ADX-Dynamic-Volatility-Optimization-System" (SMA + RSI + ADX + ATR Strategy).

FMZ source id: 483037

Source
    https://www.fmz.com/strategy/483037 (PineScript v6, FMZ last modified 2025-02-27 17:15:22).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 104-142), SMA 10 / 200, RSI 14 (50 / 50), DMI 14 / 14, ADX > 20, trail on
    long = crossover(sma10, sma200) and rsi > 50 and adx > 20; short = crossunder and rsi < 50 and adx > 20
    exit(trail_points = 30, trail_offset = 5) for each side, every bar

Interpretation choices (Pine rules in SURVEY_README.md)
    * trail_points / trail_offset are literal TICKS: on the author's market (Binance ETH_USDT, mintick 0.01, 4-minute
      ATR about 3.5 USD, price about 2,700 USD) the trail starts 0.30 USD in profit and sits 0.05 USD behind the best
      price. Ported as the house trail (as #428795) {"type": "volatility", "atr_n": 14, "k": 0.014, "anchor":
      "high_low", "activate_after": 0.00011}: k = 0.05 / 3.5 (ATR-equivalent offset) and the activation as a fraction
      of price (0.30 / 2,700). Mark trailing_stop.
    * Entries reverse (REVERSAL INTENDED). ADX as Pine's ta.dmi (as #426579). Stop module: portfolio_kwargs {} (D4).
      FREQ = "4min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close entries; the trail a house trail (approximation stated).
    2 generic: PASS, moving averages, RSI, ADX; tick distances as ATR / price fractions.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 2 % of equity quoted; the trail ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_483037_sma10_200_rsi_adx_tick_trail"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "4min"  # backtest header period: 4m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "trail_k": [0.014, 1.0],
    "fast": [10, 20],
}
DEFAULT_PARAMS = {"fast": 10, "slow": 200, "rsi_len": 14, "adx_len": 14, "adx_min": 20.0, "atr_len": 14,
                  "trail_k": 0.014, "trail_activate": 0.00011}


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


def _fixnan(v):
    """Pine fixnan: replace na by the last non-na value (past values only)."""
    out = np.array(v, dtype=float)
    for i in range(1, len(out)):
        if np.isnan(out[i]):
            out[i] = out[i - 1]
    return out


def _adx_pine(bars, di_len, adx_len):
    """Pine's built-in-style dirmov/adx: RMA smoothing, fixnan on DI+/DI-."""
    h, lo, c = bars["high"], bars["low"], bars["close"]
    up, down = h.diff(), -lo.diff()
    plus_dm = np.where(up.isna(), np.nan, np.where((up > down) & (up > 0), up, 0.0))
    minus_dm = np.where(down.isna(), np.nan, np.where((down > up) & (down > 0), down, 0.0))
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    trs = _rma(tr, di_len)
    plus = _fixnan((100 * _rma(pd.Series(plus_dm, index=h.index), di_len) / trs).to_numpy())
    minus = _fixnan((100 * _rma(pd.Series(minus_dm, index=h.index), di_len) / trs).to_numpy())
    s = plus + minus
    dx = pd.Series(np.abs(plus - minus) / np.where(s == 0, 1, s), index=h.index)
    return pd.Series(plus, index=h.index), pd.Series(minus, index=h.index), 100 * _rma(dx, adx_len)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    f, s = c.rolling(int(p["fast"])).mean(), c.rolling(int(p["slow"])).mean()
    rsi = _rsi(c, int(p["rsi_len"]))
    _, _, adx = _adx_pine(bars_df, int(p["adx_len"]), int(p["adx_len"]))
    strong = adx > p["adx_min"]
    long_e = ((f > s) & (f.shift(1) <= s.shift(1)) & (rsi > 50) & strong).astype(bool)
    short_e = ((f < s) & (f.shift(1) >= s.shift(1)) & (rsi < 50) & strong).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"trail": {"type": "volatility", "atr_n": int(p["atr_len"]), "k": float(p["trail_k"]),
                      "anchor": "high_low", "activate_after": float(p["trail_activate"])}}


def portfolio_kwargs(**params):
    return {}
