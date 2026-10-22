"""EMA 3 / 6 crossings with the source's own supertrend (ATR 3 x 1) and an RSI 10 filter, hourly bars: the cross up in the up state with RSI under 65 goes long, the cross down in the down state with RSI over 30 goes short; reversing. Each position has a 2.5 ATR stop and 4 ATR target from its fill price (the ATR of the bar before the fill; the source re-sends them with each bar's ATR, pending).
Port of FMZ strategy #475590 "多重技术指标趋势跟踪与动量RSI过滤交易策略-Multi-Technical-Indicator-Trend-Following-Strategy-with-RSI-Momentum-Filter" (ST_EMA_RSI).

FMZ source id: 475590

Source
    https://www.fmz.com/strategy/475590 (PineScript v5, FMZ last modified 2024-12-20 14:10:43).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 95-186), EMA 3 / 6; ATR 3, multiplier 1; RSI 10, 65 / 30; stop 2.5 ATR, target 4 ATR from avg
    up = high - atr, dn = low + atr;  trendUp := na(prev) ? up : close[1] > prev ? min(up, prev) : up;  trendDown := na(prev) ? dn : close[1] < prev ? max(dn, prev) : dn;  trend := close > nz(trendUp[1]) ? 1 : close < nz(trendDown[1]) ? -1 : trend[1];  crossover(ema3, ema6) and trend == 1 and rsi < 65 and size <= 0 -> entry Long;  mirror -> entry Short;  exits avg -/+ 2.5 / 4 ATR every bar

Interpretation choices (Pine rules in SURVEY_README.md)
    * The supertrend is the source's recursion as written (min / max as written; a loop with nz seeds).
      The bracket is re-sent every bar from the fill price with the current ATR: ported with the ATR of
      the bar before the fill (as fractions of the fill), the moving part kept pending (mark
      trailing_stop_pending). REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). No sizing
      code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the ATR bracket from the fill.
    2 generic: PASS, fast EMA crossings with a supertrend state and RSI filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_475590_ema3_6_cross_custom_supertrend_rsi_atr_bracket_reversal"
FAMILY = "supertrend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "fast": [3, 5],
    "slow": [6, 10],
}
DEFAULT_PARAMS = {"fast": 3, "slow": 6, "atr_len": 3, "sl_atr": 2.5, "tp_atr": 4.0}


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
    return 100 - 100 / (1 + up / dn)


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    atr = _atr(bars_df, p["atr_len"]).to_numpy(dtype=float)
    hv, lv, cv = h.to_numpy(dtype=float), lo.to_numpy(dtype=float), c.to_numpy(dtype=float)
    m = len(cv)
    tu, td, tr = np.full(m, np.nan), np.full(m, np.nan), np.zeros(m)
    for i in range(m):
        up, dn = hv[i] - atr[i], lv[i] + atr[i]
        pu = tu[i - 1] if i >= 1 else np.nan
        pdn = td[i - 1] if i >= 1 else np.nan
        c1 = cv[i - 1] if i >= 1 else np.nan
        if np.isnan(pu):
            tu[i] = up
        else:
            tu[i] = (np.nan if np.isnan(up) else min(up, pu)) if c1 > pu else up
        if np.isnan(pdn):
            td[i] = dn
        else:
            td[i] = (np.nan if np.isnan(dn) else max(dn, pdn)) if c1 < pdn else dn
        nu = 0.0 if np.isnan(pu) else pu
        nd = 0.0 if np.isnan(pdn) else pdn
        prev_t = tr[i - 1] if i >= 1 else 1.0
        tr[i] = 1.0 if cv[i] > nu else (-1.0 if cv[i] < nd else prev_t)
    t = pd.Series(tr, index=c.index)
    a = c.ewm(span=int(p["fast"]), adjust=False).mean()
    b = c.ewm(span=int(p["slow"]), adjust=False).mean()
    r = _rsi(c, 10)
    le = (a > b) & (a.shift(1) <= b.shift(1)) & (t == 1) & (r < 65)
    se = (a < b) & (a.shift(1) >= b.shift(1)) & (t == -1) & (r > 30)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    a = _atr(bars_df, p["atr_len"]).shift(1) / bars_df["open"]   # the ATR of the bar before the fill
    return {"sl_stop": float(p["sl_atr"]) * a, "tp_stop": float(p["tp_atr"]) * a}


def portfolio_kwargs(**params):
    return {}
