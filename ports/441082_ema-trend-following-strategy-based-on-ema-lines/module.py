"""Always in the market on the EMA 20 / 59 trend, 45-minute bars: long while the EMA 20 has been above the EMA 59 for two bars, short otherwise, each with a fixed 3000-tick stop from the entry (about
1.5 ATR); re-entered after a stop while the trend holds; reversing.
Port of FMZ strategy #441082 "基于EMA平均线的趋势跟踪策略Trend-Following-Strategy-Based-on-EMA-Lines" (EMA 10,20 59).

FMZ source id: 441082

Source
    https://www.fmz.com/strategy/441082 (PineScript v4, FMZ last modified 2024-02-05 14:21:18).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 169-268), EMA 10 / 20 / 59; maxLoss 3000 ticks; info boxes and signals off
    Buytrend = (ema1 and ema2 > ema3) and (ema1[1] and ema2[1] > ema3[1])  (ema1 read as a truth value)
    Buytrend -> close short, entry long, exit(loss = 3000);  not Buytrend -> close long, entry short, exit(loss = 3000)

Interpretation choices (Pine rules in SURVEY_README.md)
    * "ema1 and ..." reads the EMA 10 as a truth value (non-zero), so the trend is the EMA 20 above the EMA
      59 on this bar and the last. The stop is 3000 ticks from the entry: 300 price units at mintick 0.1 on
      the BTC reading; as an ATR multiple at the 45-minute ATR(14) reading of about 200, a stop of 1.5 ATR
      (sl = 1.5 ATR / close of the signal bar, shifted one bar inside stops() and re-based on the fill).
      After a stop the next bar enters again in the trend's direction. The profit counters and labels are
      display only. strategy.entry reverses: REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver
      D4). No sizing code. FREQ = "45min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; stop fixed at entry from signal-bar data.
    2 generic: ADAPT, tick stop -> ATR multiple.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_441082_ema20_59_always_in_tick_stop"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "45min"  # backtest header period: 45m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "ema2": [20, 40],
    "ema3": [59, 100],
}
DEFAULT_PARAMS = {"ema2": 20, "ema3": 59, "atr_len": 14, "sl_atr": 1.5}


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


def _sl(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return float(p["sl_atr"]) * _rma(tr, int(p["atr_len"])) / c


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    e2 = c.ewm(span=int(p["ema2"]), adjust=False).mean()
    e3 = c.ewm(span=int(p["ema3"]), adjust=False).mean()
    up = e2 > e3
    bt = (up & up.shift(1, fill_value=False)).to_numpy()
    sl = _sl(bars_df, p).to_numpy()
    ov = bars_df["open"].to_numpy(dtype=float)
    hv, lv = bars_df["high"].to_numpy(dtype=float), bars_df["low"].to_numpy(dtype=float)
    m = len(ov)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, entry_i, s_ = 0, -1, np.nan
    for i in range(m):
        if pos != 0 and i >= entry_i:
            x = ov[entry_i]
            if pos == 1 and lv[i] <= x * (1 - s_):
                pos = 0
            elif pos == -1 and hv[i] >= x * (1 + s_):
                pos = 0
        want = 1 if bt[i] else -1
        if pos != want and i + 1 < m and not np.isnan(sl[i]):
            if want == 1:
                le[i] = True
            else:
                se[i] = True
            pos, entry_i, s_ = want, i + 1, sl[i]
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": _sl(bars_df, p).shift(1)}


def portfolio_kwargs(**params):
    return {}
