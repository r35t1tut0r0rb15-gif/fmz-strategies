"""RSI of a double EMA against its EMA, inside 04:00-15:00 UTC, 1-hour bars: the RSI 4 of EMA(EMA(close, 21), 21) crossing over its EMA 4 goes long, crossing under short; a trailing stop that starts
after a small gain and trails close behind; everything closes outside the session; reversing.
Port of FMZ strategy #440437 "双指数移动平均线RSI交易策略Double-Exponential-Moving-Average-RSI-Trading-Strategy" ([STRATEGY][RS]DemaRSI V0).

FMZ source id: 440437

Source
    https://www.fmz.com/strategy/440437 (PineScript v2, FMZ last modified 2024-01-30 15:44:11).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 142-177), MA 21, RSI 4, smoothing 4; size 1; target and stop 100000 points; trail 150 / 150 points; session 0400-1500
    ma = ema(ema(close, 21), 21);  marsi = rsi(ma, 4);  smooth = ema(marsi, 4);  in session: crossover(marsi, smooth) -> entry buy, crossunder -> entry sel
    strategy.exit(profit = 100000, loss = 100000, trail_points = 150, trail_offset = 150) for each side;  close_all when not in session

Interpretation choices (Pine rules in SURVEY_README.md)
    * The session is read on the UTC bar open: bars opening 04:00-14:00 are inside. Criterion 2: on
      1-hour BTC (0.1 tick, ATR about 150 USD near 42000) the trail activates after 150 ticks (15 USD,
      about 0.00036 of the price) and trails 150 ticks (about 0.1 ATR) behind the best price: the house
      trail {"type": "volatility", "atr_n": 14, "k": 0.1, "anchor": "high_low", "activate_after":
      0.00036} (stated approximation, as #437390; mark trailing_stop). The 100000-tick target and stop
      (about 67 ATR) are out of reach; they are kept as ATR(14) multiples of the signal bar, shifted one
      bar inside stops(). strategy.entry reverses: REVERSAL INTENDED. Stop module: portfolio_kwargs {}
      (driver D4). The size 1 and capital are sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the trail is a house trail (approximation stated).
    2 generic: ADAPT, tick trail and bracket -> house trail and ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: size 1 and capital are sizing.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: entries on bars opening 04:00-14:00 UTC; close_all on the other bars (bar open time).
REVERSAL INTENDED.

Marks: trailing_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_440437_dema_rsi_cross_session_trail"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "trail_k": [0.1, 1.0],
    "ma_length": [21, 10],
}
DEFAULT_PARAMS = {"trail_k": 0.1, "ma_length": 21, "rsi_length": 4, "rsi_smooth": 4, "trail_activate": 0.00036,
                  "far_k": 66.7, "atr_len": 14, "sess_start": 4, "sess_end": 15}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = int(p["ma_length"])
    ma = c.ewm(span=n, adjust=False).mean().ewm(span=n, adjust=False).mean()
    mr = _rsi(ma, int(p["rsi_length"]))
    sm = mr.ewm(span=int(p["rsi_smooth"]), adjust=False).mean()
    hour = bars_df.index.tz_convert("UTC").hour
    sess = pd.Series((hour >= int(p["sess_start"])) & (hour < int(p["sess_end"])), index=c.index)
    buy = sess & (mr > sm) & (mr.shift(1) <= sm.shift(1))
    sel = sess & (mr < sm) & (mr.shift(1) >= sm.shift(1))
    out = ~sess
    return buy, out, sel, out.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    far = (float(p["far_k"]) * _atr(bars_df, p["atr_len"]) / bars_df["close"]).shift(1)
    return {"sl_stop": far, "tp_stop": far.copy(),
            "trail": {"type": "volatility", "atr_n": int(p["atr_len"]), "k": float(p["trail_k"]),
                      "anchor": "high_low", "activate_after": float(p["trail_activate"])}}


def portfolio_kwargs(**params):
    return {}
