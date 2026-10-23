"""Three-hour bars: volume 50 % above its 20-bar average with RSI 14 under 70 and either the close crossing over the SMA 20 with MACD above its signal or MACD crossing over its signal with the close above the SMA, goes long; the mirror (RSI above 30) goes short; a close past the SMA, an RSI beyond 70 / 30, or a close 0.5 % beyond the entry price closes each, but only on a weekday other than that of the last signal; reversing.
Port of FMZ strategy #440962 "趋势顺势RSI波动捕捉策略Trend-Riding-RSI-Swing-Capture-Strategy" (SwingSync RSI (str0zzapreti)).

FMZ source id: 440962

Source
    https://www.fmz.com/strategy/440962 (PineScript v5, FMZ last modified 2024-02-04 10:48:38).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 151-244), SMA 20; RSI 14, 70 / 30; MACD 12 / 26 / 9; volume SMA 20 x 1.5; stop 1 % with 0.5 % "slippage"; qty 1
    longCondition = volume > sma(volume, 20) x 1.5 and rsi < 70 and ((crossover(close, ma) and macd > signal) or (crossover(macd, signal) and close > ma)) -> entry Long (qty 1);  short mirror
    last_trade_day := dayofweek on any signal;  can_exit_trade = dayofweek != last_trade_day;  long and can_exit: close < avg x 0.99 x 1.005 or crossunder(close, ma) or rsi > 70 -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop level is avg x (1 - 1 %) x (1 + 0.5 %) = avg x 0.99495 for a long (avg x 1.00495 for a
      short), a close-based test at the bar close, in the signals; the average price is the fill. The
      weekday rule blocks every exit on the weekday of the latest signal, even days later (weird case);
      weekdays are read in UTC (header exchange time). The computed qty is never used (qty 1 is sizing). A
      close acts only on a position the bar's entries leave unchanged. REVERSAL INTENDED. FREQ = "3h" from
      the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; close-based stop in the signals.
    2 generic: PASS, volume-confirmed SMA / MACD crossings with RSI limits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: entry qty 1 unit (the equity-based qty is unused), not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) against 1.5 x its SMA 20; exchange volume to be compared later (Austin, 2026-10-23).
Session open: weekdays in UTC (header exchange time) for the exit rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_440962_volume_sma_macd_cross_rsi_weekday_exit_3h_reversal"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ma_period": [20, 50],
    "vol_pct": [50, 25],
}
DEFAULT_PARAMS = {"ma_period": 20, "stop_pct": 1.0, "slippage": 0.5, "rsi_len": 14, "ob": 70.0, "os": 30.0,
                  "vol_len": 20, "vol_pct": 50}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, c, v = bars_df["open"], bars_df["close"], bars_df["volume"]
    ma = c.rolling(int(p["ma_period"])).mean()
    rsi = _rsi(c, int(p["rsi_len"]))
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    vol_ok = v > v.rolling(int(p["vol_len"])).mean() * (1 + float(p["vol_pct"]) / 100)
    c_up = (c > ma) & (c.shift(1) <= ma.shift(1))
    c_dn = (c < ma) & (c.shift(1) >= ma.shift(1))
    m_up = (macd > sig) & (macd.shift(1) <= sig.shift(1))
    m_dn = (macd < sig) & (macd.shift(1) >= sig.shift(1))
    ob, os_ = float(p["ob"]), float(p["os"])
    lg = (vol_ok & (rsi < ob) & ((c_up & (macd > sig)) | (m_up & (c > ma)))).to_numpy()
    sh = (vol_ok & (rsi > os_) & ((c_dn & (macd < sig)) | (m_dn & (c < ma)))).to_numpy()
    ex_l = (c_dn | (rsi > ob)).to_numpy()
    ex_s = (c_up | (rsi < os_)).to_numpy()
    k_l = (1 - float(p["stop_pct"]) / 100) * (1 + float(p["slippage"]) / 100)
    k_s = (1 + float(p["stop_pct"]) / 100) * (1 - float(p["slippage"]) / 100)
    dow = np.asarray(c.index.dayofweek)
    ov, cv = o.to_numpy(dtype=float), c.to_numpy(dtype=float)
    m = len(lg)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    tgt, px, last_day = 0, np.nan, -1
    for i in range(m):
        if i > 0 and (le[i - 1] or se[i - 1]):
            px = ov[i]                                   # the fill = the average price
        held = tgt
        if lg[i] or sh[i]:
            last_day = dow[i]
        can_exit = dow[i] != last_day
        new = tgt
        if lg[i] and new != 1:
            new = 1
        if sh[i] and new != -1:
            new = -1
        if new == held and can_exit:
            if held == 1 and (cv[i] < px * k_l or ex_l[i]):
                new = 0
            elif held == -1 and (cv[i] > px * k_s or ex_s[i]):
                new = 0
        if new != tgt and i + 1 < m:
            if new == 1:
                le[i] = True
            elif new == -1:
                se[i] = True
            elif tgt == 1:
                lx[i] = True
            else:
                sx[i] = True
            tgt = new
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
