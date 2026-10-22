"""Rising averages long-only trend entries, 10-minute bars, long only: from the script's flat flag, the SMA 200 not falling for 10 bars, the MACD line for 3, the EMA 20 for 2 and the SMA 100 for 3, with the
EMA 20 above the SMA 100 and the SMA 100 under the close, buys; a close 5 % under the signal close or the EMA 20 crossing under the SMA 100 (one bar back) closes.
Port of FMZ strategy #439200 "Multi factor Moving Average Trend Following Strategy" (BTC_Long_Only_TV01_200507).

FMZ source id: 439200

Source
    https://www.fmz.com/strategy/439200 (PineScript v4, FMZ last modified 2024-01-18 12:07:52).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 156-284), EMA 20, SMA 100 / 200; MACD 12 / 26 / 7; stop 5 %; position 1000 / close; window true
    IsRising(x, n) = no step down over the last n bars;  not open and smaSlow rising 10 and macd rising 3 and ema rising 2 and sma rising 3 and ema > sma and sma < close -> entry myPosition, stop := close x 0.95, open := true
    open and (close <= stop or crossunder(ema[1], sma[1])) -> close myPosition, open := false

Interpretation choices (Pine rules in SURVEY_README.md)
    * The script's own flag (bPositionOpened) gates the entries and the closes; the stop is a close test
      against 95 % of the signal close (an order-free level). A close on the entry bar acts on the
      position held at that bar close (none), as written; the flag is still cleared. Long only. The
      position size is sizing. FREQ = "10min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; close-tested stop.
    2 generic: PASS, slope tests of averages and MACD.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the 1000 / close position size stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND428579 (2 members, best partner #428579, Jaccard 0.733); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_439200_rising_averages_long_flagged"
FAMILY = "trend_confluence"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "10min"  # backtest header period: 10m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "stop_loss": [5.0, 2.0],
    "sma_len": [100, 50],
}
DEFAULT_PARAMS = {"stop_loss": 5.0, "sma_len": 100, "ema_len": 20, "sma_slow": 200}


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


def _rising(x, n):
    """IsRising(data, n): no data[k] > data[k - 1] for k = 1..n (no step down)."""
    ok = pd.Series(True, index=x.index)
    for k in range(1, n + 1):
        ok &= ~(x.shift(k) > x.shift(k - 1))
    return ok


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    ema = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    sma = c.rolling(int(p["sma_len"])).mean()
    sma_s = c.rolling(int(p["sma_slow"])).mean()
    entry_ok = (_rising(sma_s, 10) & _rising(macd, 3) & _rising(ema, 2) & _rising(sma, 3)
                & (ema > sma) & (sma < c)).to_numpy()
    e1, s1 = ema.shift(1), sma.shift(1)
    xu = ((e1 < s1) & (e1.shift(1) >= s1.shift(1))).to_numpy()
    cv = c.to_numpy(dtype=float)
    sl = float(p["stop_loss"]) / 100
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    flag, stop, pos, pend = False, 0.0, 0, None
    for i in range(m):
        if pend is not None:                             # orders of the last bar fill at this open
            pos, pend = pend, None
        if not flag and entry_ok[i]:
            stop = cv[i] * (1 - sl)
            flag = True
            if pos == 0 and i + 1 < m:
                le[i], pend = True, 1
        if flag and (cv[i] <= stop or xu[i]):
            if pos == 1:
                lx[i], pend = True, 0
            flag = False
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
