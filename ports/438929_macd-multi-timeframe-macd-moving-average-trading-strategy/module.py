"""1-minute RSI crossings read on 3-hour bars with pin-bar exits and a tick bracket, 3-hour bars: the RSI 14 of the bar's last minute crossing up through 35 goes long, down through 65 goes short (reversing);
a bearish pin bar closes a long, a bullish one a short; each trade has a tick stop and target, re-expressed as ATR multiples.
Port of FMZ strategy #438929 "多时间周期MACD均线交易策略Multi-Timeframe-MACD-Moving-Average-Trading-Strategy" (JMRCS).

FMZ source id: 438929

Source
    https://www.fmz.com/strategy/438929 (PineScript v2, FMZ last modified 2024-01-16 14:06:10).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 231-407), resolution "1" (custom, on a 3-hour chart), large time frame 15 (display); RSI 14 at 65 / 35; pin bars 66 / 72 %, lookback 6, body factor 3; take profit 1500, stop 100 (ticks); trailing off
    rsi1 = security(tickerid, "1", rsi(close, 14));  enterLong = rsi1[1] < 35 and rsi1 > 35;  enterShort = rsi1[1] > 65 and rsi1 < 65
    exitLong = bearish pin bar (pIHammer);  exitShort = bullish pin bar (pHammer);  exit(profit = 1500, loss = 100) for each side;  MACD averages, fractals and other candles: display

Interpretation choices (Pine rules in SURVEY_README.md)
    * The 1-minute RSI requested from a 3-hour chart is the value of the bar's LAST minute (a lower time
      frame returns its last bar inside the chart bar); the RSI 14 runs on the minute closes. The 15-minute
      RSI only colours the background. Pin bars follow the source (body over 3 / 10000 of the high; wick
      shares 66 / 72 %; 6-bar extremes include the current bar).
    * Criterion 2: the tick bracket is re-expressed as sl_stop = k_sl x ATR(14) / close of the signal bar
      (shifted one bar inside stops(), re-based on the fill) with a target 15 times it; 0.029 is the
      reading (100 ticks of 0.1 = 10 on BTC against a 3-hour ATR near 350), 1.0 a wider stop. The closes
      act on the position held at the bar close. strategy.entry reverses: REVERSAL INTENDED. Stop module:
      portfolio_kwargs {} (driver D4). Stops on 3-hour bars: mark coarse_bar_stop. No sizing code.
      FREQ = "3h" from the backtest header (bars on UTC multiples of 3 hours).

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: ADAPT, tick bracket -> ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the tick inputs stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_438929_minute_rsi_cross_pin_bar_exit"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "k_sl": [0.029, 1.0],
    "rsi_len": [14, 28],
}
DEFAULT_PARAMS = {"k_sl": 0.029, "rsi_len": 14, "up_line": 65.0, "low_line": 35.0, "pct_p": 66, "pct_rp": 72,
                  "pblb": 6, "body_factor": 3.0, "tp_ratio": 15.0, "atr_len": 14}


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


def precompute(raw_1m_df, symbol_key, **params):
    p = {**DEFAULT_PARAMS, **params}
    bars = _resample(raw_1m_df, FREQ)
    c1 = raw_1m_df["close"].dropna()
    r1 = _rsi(c1, int(p["rsi_len"]))
    key = r1.index.floor(FREQ)
    last = r1[~pd.Index(key).duplicated(keep="last")]   # the value of each bar's last minute
    last.index = key[~pd.Index(key).duplicated(keep="last")]
    bars["rsi_1m"] = last.reindex(bars.index)
    return bars


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    r = bars_df["rsi_1m"]
    ul, ll = float(p["up_line"]), float(p["low_line"])
    enter_l = ((r.shift(1) < ll) & (r > ll)).to_numpy()
    enter_s = ((r.shift(1) > ul) & (r < ul)).to_numpy()
    rng = h - lo
    pcp, pcr = float(p["pct_p"]) / 100, float(p["pct_rp"]) / 100
    pbody = (o - c).abs() / np.maximum(h, lo) * 10000 > float(p["body_factor"])
    k = int(p["pblb"])
    r_up = (o > h - rng * (1 - pcr)) & (c > h - rng * (1 - pcr)) & (lo <= lo.rolling(k).min())
    r_dn = (o < h - rng * pcr) & (c < h - rng * pcr) & (h >= h.rolling(k).max())
    bar_dn = (o < h - rng * pcp) & (c < h - rng * pcp)
    bar_up = (o > lo + rng * pcp) & (c > lo + rng * pcp)
    hammer = (pbody & bar_up & ~r_up & ~r_dn).to_numpy()
    ihammer = (pbody & bar_dn & ~r_up & ~r_dn).to_numpy()
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if enter_l[i] and pos != 1 and i + 1 < m:
            le[i], pos = True, 1
        elif enter_s[i] and pos != -1 and i + 1 < m:
            se[i], pos = True, -1
        elif pos == 1 and ihammer[i]:
            lx[i], pos = True, 0
        elif pos == -1 and hammer[i]:
            sx[i], pos = True, 0
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    f = float(p["k_sl"]) * _atr(bars_df, p["atr_len"]) / bars_df["close"]
    return {"sl_stop": f.shift(1), "tp_stop": (float(p["tp_ratio"]) * f).shift(1)}


def portfolio_kwargs(**params):
    return {}
