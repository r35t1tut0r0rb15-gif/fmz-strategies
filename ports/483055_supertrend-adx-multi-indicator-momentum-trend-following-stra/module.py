"""SuperTrend 3 / 14 up-trend with ADX 14 over 14 and RSI 14 outside 40-60, 5-minute bars, long only: the condition goes long, the SuperTrend turning down closes.
Port of FMZ strategy #483055 "多指标交叉动量趋势跟踪策略基于Supertrend与ADX双重确认的量化交易系统-Multi-Indicator-Momentum-Trend-Following-Strategy-Quantitative-Trading-System-Based-on-Supertrend-and-ADX-Dual-Confirmation" (Supertrend + ADX Strategy).

FMZ source id: 483055

Source
    https://www.fmz.com/strategy/483055 (PineScript v6, FMZ last modified 2025-02-27 17:07:46).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 115-157), DMI 14 / 14, ADX threshold 14; SuperTrend factor 3, period 14; RSI 14
    direction == -1 and adx > 14 and (rsi < 40 or rsi > 60) -> entry Long;  direction == 1 -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * direction -1 is Pine's up-trend. The entry is a state; a repeat while long adds nothing. ta.dmi is
      Wilder's DMI. Long only. No sizing code. FREQ = "5min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SuperTrend direction with ADX / RSI filters.
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

NAME = "fmz_483055_supertrend3_14_up_adx14_rsi_outside_40_60_long"
FAMILY = "supertrend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "supertrend_factor": [3.0, 2.0],
    "supertrend_period": [14, 10],
}
DEFAULT_PARAMS = {"supertrend_factor": 3.0, "supertrend_period": 14, "di_length": 14, "adx_smoothing": 14,
                  "adx_threshold": 14.0, "rsi_length": 14}


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


def _tr(bars_df):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    return pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)


def _supertrend(bars_df, factor, period):
    """ta.supertrend (Pine reference implementation): returns (line, direction), -1 = up-trend."""
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    atr = _rma(_tr(bars_df), period).to_numpy()
    src = ((h + lo) / 2).to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    lower, upper = np.full(m, np.nan), np.full(m, np.nan)
    line, direc = np.full(m, np.nan), np.full(m, np.nan)
    for i in range(m):
        lb, ub = src[i] - factor * atr[i], src[i] + factor * atr[i]
        plb = lower[i - 1] if i >= 1 and not np.isnan(lower[i - 1]) else 0.0
        pub = upper[i - 1] if i >= 1 and not np.isnan(upper[i - 1]) else 0.0
        c1 = cv[i - 1] if i >= 1 else np.nan
        lower[i] = lb if (lb > plb or c1 < plb) else plb
        upper[i] = ub if (ub < pub or c1 > pub) else pub
        if i == 0 or np.isnan(atr[i - 1]):
            d = 1
        elif line[i - 1] == pub:
            d = -1 if cv[i] > upper[i] else 1
        else:
            d = 1 if cv[i] < lower[i] else -1
        direc[i] = d
        line[i] = lower[i] if d == -1 else upper[i]
    return pd.Series(line, index=bars_df.index), pd.Series(direc, index=bars_df.index)


def _adx(bars_df, n, sm):
    h, lo = bars_df["high"], bars_df["low"]
    tr = _tr(bars_df)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]
    up, dn = h.diff(), -lo.diff()
    pdm = up.where((up > dn) & (up > 0), 0.0)
    mdm = dn.where((dn > up) & (dn > 0), 0.0)
    trs = _rma(tr, n)
    pdi, mdi = 100 * _rma(pdm, n) / trs, 100 * _rma(mdm, n) / trs
    s = pdi + mdi
    return _rma(100 * (pdi - mdi).abs() / s.where(s > 0), sm)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    d = _supertrend(bars_df, float(p["supertrend_factor"]), int(p["supertrend_period"]))[1]
    adx = _adx(bars_df, int(p["di_length"]), int(p["adx_smoothing"]))
    r = _rsi(c, int(p["rsi_length"]))
    le = (d == -1) & (adx > float(p["adx_threshold"])) & ((r < 40) | (r > 60))
    lx = d == 1
    false = pd.Series(False, index=c.index)
    return le, lx & ~le, false, false.copy()


def portfolio_kwargs(**params):
    return {}
