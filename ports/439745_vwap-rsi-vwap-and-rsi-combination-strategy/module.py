"""One-minute bars, long only: the EMA 50 above the EMA 200, an up bar closing above the session VWAP, and the RSI 3 under 10 on any of the previous 10 bars goes long; the RSI 3 crossing under 90, or a close 5 % under the entry price, closes it.
Port of FMZ strategy #439745 "VWAP和RSI组合策略VWAP-and-RSI-Combination-Strategy" (VWAP and RSI strategy [EEMANI] (mohanee)).

FMZ source id: 439745

Source
    https://www.fmz.com/strategy/439745 (PineScript v4, FMZ last modified 2024-01-23 14:37:22).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 139-195), EMA 50 / 200; RSI 3, buy line 10, sell line 90; vwap(hlc3); stop loss 5 %
    longCondition = ema50 > ema200 and close > open and close > vwap(hlc3);  rsiDipped = rsi3[1] < 10 or ... or rsi3[10] < 10 -> entry
    close when crossunder(rsi3, 90);  close when close < position_avg_price x 0.95

Interpretation choices (Pine rules in SURVEY_README.md)
    * vwap(hlc3) is the session VWAP, anchored at the broker-day start (as earlier ports). Both exits
      are closes at the bar close (the stop compares the close with the entry fill price), so they fill
      at the next open, from the fill bar on. An entry while long adds nothing. Long only. No sizing
      code. FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; close-based stop in the signals.
    2 generic: PASS, trend-filtered VWAP breaks after an RSI 3 dip.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data) as the session VWAP's weights; exchange volume to be compared later (Austin, 2026-10-23).
Session open: session VWAP anchored at the broker day (17:00 America/New_York).
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_439745_ema50_200_vwap_rsi3_dip_close_stop_1m_long_only"
FAMILY = "vwap_breakout"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_buy": [10, 20],
    "stop_pct": [0.05, 0.02],
}
DEFAULT_PARAMS = {"long_ema": 200, "short_ema": 50, "rsi_len": 3, "rsi_buy": 10, "rsi_sell": 90, "stop_pct": 0.05}


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


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


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
    o, h, lo, c, v = (bars_df[k] for k in ("open", "high", "low", "close", "volume"))
    day = broker_day(c.index)
    hlc3 = (h + lo + c) / 3
    cv = v.groupby(day).cumsum()
    vwap = (hlc3 * v).groupby(day).cumsum() / cv.where(cv != 0)
    el = c.ewm(span=int(p["long_ema"]), adjust=False).mean()
    es = c.ewm(span=int(p["short_ema"]), adjust=False).mean()
    r = _rsi(c, int(p["rsi_len"]))
    dipped = r.shift(1).rolling(10, min_periods=1).min() < float(p["rsi_buy"])
    entry = ((es > el) & (c > o) & (c > vwap) & dipped).to_numpy()
    rs = float(p["rsi_sell"])
    tp = ((r < rs) & (r.shift(1) >= rs)).to_numpy()
    ov, cvv = o.to_numpy(dtype=float), c.to_numpy(dtype=float)
    k = 1 - float(p["stop_pct"])
    m = len(entry)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, pend, px = 0, False, np.nan
    for i in range(m):
        if pend:
            pos, pend, px = 1, False, ov[i]
        if pos == 1:
            if tp[i] or cvv[i] < px * k:
                lx[i], pos = True, 0
        elif not pend and entry[i] and i + 1 < m:
            le[i], pend = True, True
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
