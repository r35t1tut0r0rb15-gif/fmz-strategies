"""Four-hour bars, long only: from flat, with the EMA 8 > 13 > 21 > 34 > 55 ribbon, RSI 14 between 40 and 70 and the stochastic 14 under 80, the close crossing over the (undisplaced) senkou span A or a momentum set (close, SMA 21, RSI and OBV all rising, OBV above its SMA 14) goes long; the SMA 21 crossing under the SMA 26, the close crossing under the SMA 52 "span B", the EMA 13 under the EMA 55, RSI above 70 or the stochastic above 95 closes it.
Port of FMZ strategy #440526 "Multi factor Quantitative Trading Strategy" (МТС Ишимоку TP/SL ADX RSI OBV (Ichimoku / EMA ribbon / RSI / stochastic / OBV)).

FMZ source id: 440526

Source
    https://www.fmz.com/strategy/440526 (PineScript v5, FMZ last modified 2024-01-31 13:55:37).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 169-290), SMA 21 / 26; tenkan 9, kijun 26, span B 52 (SMA of close); RSI 14; OBV SMA 14; EMA 8 / 13 / 21 / 34 / 55; stochastic 14; longs on, shorts off
    enter_long = (crossover(close, senkou_span_a) or is_up) and longEmaCondition and longRsiCondition and longStochasticCondition and position_size == 0
    exit_long = crossunder(fast_ma, slow_ma) or crossunder(close, senkou_span_b) or enter_short or (exitLongEma or exitLongRsi or exitLongStoch) and position_size > 0

Interpretation choices (Pine rules in SURVEY_README.md)
    * As written: tenkan / kijun are SMAs of high + low halved (not midpoints), span A is not displaced
      and span B is an SMA 52 of the close. is_up = close[1] > close[3], close > SMA 21, SMA 21 one bar
      ago above three bars ago, RSI one bar ago above three bars ago, RSI > 50, OBV one bar ago above three
      bars ago and OBV above its SMA 14 (OBV = cumulative sign of the change x volume, the first na change
      adds nothing). Shorts are off (is_short_enable 0); enter_short needs a flat position, so it never
      closes a long. Long only. No sizing code. FREQ = "4h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA ribbon trend with cloud / momentum triggers and multi-condition exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the OBV trend tests; exchange volume to be compared later (Austin, 2026-10-23).
Session open: none (24 h).
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_440526_ema_ribbon_cloud_obv_momentum_4h_long_only"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [21, 10],
    "obv_len": [14, 28],
}
DEFAULT_PARAMS = {"fast": 21, "slow": 26, "tenkan": 9, "kijun": 26, "senkou": 52, "rsi_len": 14, "obv_len": 14}


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
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


def _rsi(x, n):
    d = x.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    out = 100 - 100 / (1 + up / dn.where(dn != 0))
    return out.where(up != 0, 0.0).where(dn != 0, 100.0).where(up.notna() & dn.notna())


def _over(a, b):
    return (a > b) & (a.shift(1) <= b.shift(1))


def _under(a, b):
    return (a < b) & (a.shift(1) >= b.shift(1))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, v = (bars_df[k] for k in ("high", "low", "close", "volume"))
    fl = int(p["fast"])
    fast, slow = c.rolling(fl).mean(), c.rolling(int(p["slow"])).mean()
    tenkan = (h + lo).rolling(int(p["tenkan"])).mean() / 2
    kijun = (h + lo).rolling(int(p["kijun"])).mean() / 2
    span_a = (tenkan + kijun) / 2
    span_b = c.rolling(int(p["senkou"])).mean()
    rl = int(p["rsi_len"])
    rsi = _rsi(c, rl)
    obv = (np.sign(c.diff()) * v).fillna(0.0).cumsum()
    obv_ma = obv.rolling(int(p["obv_len"])).mean()
    is_up = ((c.shift(1) > c.shift(3)) & (c > fast) & (fast.shift(1) > fast.shift(3)) & (rsi.shift(1) > rsi.shift(3))
             & (rsi > 50) & (obv.shift(1) > obv.shift(3)) & (obv > obv_ma))
    e = {n: c.ewm(span=n, adjust=False).mean() for n in (8, 13, 21, 34, 55)}
    ribbon = (e[8] > e[13]) & (e[13] > e[21]) & (e[21] > e[34]) & (e[34] > e[55])
    rsi14 = _rsi(c, 14)
    hh, ll = h.rolling(14).max(), lo.rolling(14).min()
    k = 100 * (c - ll) / (hh - ll).where(hh != ll)
    long_ok = ribbon & (rsi14 < 70) & (rsi14 > 40) & (k < 80)
    enter = ((_over(c, span_a) | is_up) & long_ok).to_numpy()
    leave = (_under(fast, slow) | _under(c, span_b) | (e[13] < e[55]) | (rsi14 > 70) | (k > 95)).to_numpy()
    m = len(enter)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if pos == 1 and leave[i]:
            lx[i], pos = True, 0
        elif pos == 0 and enter[i]:
            le[i], pos = True, 1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
