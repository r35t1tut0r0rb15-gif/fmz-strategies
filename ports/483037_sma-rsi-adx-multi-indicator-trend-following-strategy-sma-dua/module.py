"""SMA 10 / 200 crossings with RSI 14 beyond 50 and ADX 14 over 20, 4-minute bars: the up-cross goes long and the down-cross goes short, each followed by a tight trailing stop (5 ticks behind the best price once 30 ticks in profit, read as percents); reversing.
Port of FMZ strategy #483037 "多重指标趋势跟踪策略基于SMA双线交叉结合RSI和ADX的动态波动率优化系统-Multi-Indicator-Trend-Following-Strategy-SMA-Dual-Line-Crossover-with-RSI-and-ADX-Dynamic-Volatility-Optimization-System" (SMA + RSI + ADX + ATR Strategy).

FMZ source id: 483037

Source
    https://www.fmz.com/strategy/483037 (PineScript v6, FMZ last modified 2025-02-27 17:15:22).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 100-149), SMA 10 / 200; RSI 14 / 50 / 50; DMI 14 / 14, ADX over 20; ATR 14 (unused); trail_points 30, trail_offset 5; 2 % of equity
    crossover(sma10, sma200) and rsi > 50 and adx > 20 -> entry BUY;  crossunder and rsi < 50 and adx > 20 -> entry SELL
    every bar: exit BUY / SELL (trail_points = 30, trail_offset = 5)

Interpretation choices (Pine rules in SURVEY_README.md)
    * trail_points / trail_offset are ticks: on the header's ETH_USDT (tick 0.01, about 2700 USDT in the
      header window) 30 ticks of profit start a trail 5 ticks behind the best price. Read as the house
      percent trail 0.05 / 2700 = 1.852e-05 behind the best price (anchor high_low), active after
      0.30 / 2700 = 1.111e-04 of gain (as #458242, at the header's prices); mark trailing_stop. The ATR is
      computed but feeds nothing. An entry on the other side reverses (REVERSAL INTENDED). Stop module:
      portfolio_kwargs {} (driver D4). ta.dmi is Wilder's DMI. The 2 % of equity size is sizing.
      FREQ = "4min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; house percent trail.
    2 generic: ADAPT, tick trail read as percents at the header's ETH prices.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 2 % of equity stored, not ported.
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

NAME = "fmz_483037_sma10_200_cross_rsi50_adx20_tick_trail_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "4min"  # backtest header period: 4m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "trail_pct": [1.852e-05, 0.005],
    "sma_fast": [10, 20],
}
DEFAULT_PARAMS = {"trail_pct": 1.852e-05, "sma_fast": 10, "sma_slow": 200, "activate_ratio": 6.0,
                  "rsi_length": 14, "adx_length": 14, "rsi_level": 50, "adx_min": 20}


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
    r = r.where(dn != 0, 100.0).where(up != 0, 0.0)
    return r.where(up.notna() & dn.notna())


def _adx(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]
    up, dn = h.diff(), -lo.diff()
    pdm = up.where((up > dn) & (up > 0), 0.0)
    mdm = dn.where((dn > up) & (dn > 0), 0.0)
    trs = _rma(tr, n)
    pdi, mdi = 100 * _rma(pdm, n) / trs, 100 * _rma(mdm, n) / trs
    s = pdi + mdi
    return _rma(100 * (pdi - mdi).abs() / s.where(s > 0), n)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    f, s = c.rolling(int(p["sma_fast"])).mean(), c.rolling(int(p["sma_slow"])).mean()
    r = _rsi(c, int(p["rsi_length"]))
    adx = _adx(bars_df, int(p["adx_length"]))
    lvl, amin = float(p["rsi_level"]), float(p["adx_min"])
    le = (f > s) & (f.shift(1) <= s.shift(1)) & (r > lvl) & (adx > amin)
    se = (f < s) & (f.shift(1) >= s.shift(1)) & (r < lvl) & (adx > amin)
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    t = float(p["trail_pct"])
    return {"trail": {"type": "percent", "pct": t, "anchor": "high_low",
                      "activate_after": t * float(p["activate_ratio"])}}


def portfolio_kwargs(**params):
    return {}
