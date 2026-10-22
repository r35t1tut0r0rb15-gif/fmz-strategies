"""RSI pullbacks in an EMA 200 trend with an ATR bracket, 5-minute bars: above the EMA 200, an RSI 10 crossing back over 40 goes long; below it, an RSI crossing back under 60 goes short; each trade has a stop
4 ATR(14) away and a target at twice that distance; reversing.
Port of FMZ strategy #439244 "双重EMA与RSI结合的趋势跟踪策略Dual-EMA-and-RSI-Combined-Trend-Tracking-Strategy" (Risk Management Strategy Template).

FMZ source id: 439244

Source
    https://www.fmz.com/strategy/439244 (PineScript v5, FMZ last modified 2024-01-18 15:51:06).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 203-393), EMA 200; RSI 10, overbought 60, oversold 40; stop ATR 14 x 4; risk : reward 1 : 2; risk 1 %; date range 2022-01-01 to 2100-01-01
    goLong = close > ema and crossover(rsi, 40);  goShort = close < ema and crossunder(rsi, 60);  openLong = goLong and not inLong;  openShort mirror -> strategy.entry (reverses)
    on entry: lossPoints = ticks of 4 atr(14) from the signal close, profitPoints = 2 x that;  strategy.exit("TP/SL", profit = profitPoints, loss = lossPoints) for any position

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket distances are fixed on the signal bar and measured from the fill: sl_stop = 4 x ATR(14)
      / close of the signal bar, tp_stop = 2 x that, shifted one bar inside stops() and re-based on the
      fill. The script's own in-trade flags (judged on levels from the signal close) are read as the
      position; a same-side signal while in a position is ignored. The date range covers the data
      (#436533). strategy.entry reverses: REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver
      D4). The risk-based quantity is sizing; the commission is a cost. FREQ = "5min" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: PASS, EMA trend, RSI crossings and ATR distances.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the risk percent, capital and commission stored.
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

NAME = "fmz_439244_ema200_rsi_pullback_atr_bracket"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_mult": [4.0, 2.0],
    "risk_reward": [2.0, 1.0],
}
DEFAULT_PARAMS = {"sl_mult": 4.0, "risk_reward": 2.0, "ema_len": 200, "rsi_len": 10, "overbought": 60,
                  "oversold": 40, "atr_len": 14}


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
    up = _rma(d.clip(lower=0), n)
    dn = _rma((-d).clip(lower=0), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100.0 - 100.0 / (1.0 + up / dn)
    r = r.where(up != 0, 0.0).where(dn != 0, 100.0)    # Pine: down == 0 -> 100, else up == 0 -> 0
    return r.where(up.notna() & dn.notna())


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    e = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    r = _rsi(c, int(p["rsi_len"]))
    os_, ob = float(p["oversold"]), float(p["overbought"])
    up = (c > e) & (r > os_) & (r.shift(1) <= os_)
    dn = (c < e) & (r < ob) & (r.shift(1) >= ob)
    false = pd.Series(False, index=c.index)
    return up, false, dn, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    sl = float(p["sl_mult"]) * _atr(bars_df, p["atr_len"]) / bars_df["close"]
    sl = sl.where(sl > 0)
    return {"sl_stop": sl.shift(1), "tp_stop": (float(p["risk_reward"]) * sl).shift(1)}


def portfolio_kwargs(**params):
    return {}
