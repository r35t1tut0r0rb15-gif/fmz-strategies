"""Heikin-Ashi SAR flips with EMA 200 and RSI, 3-hour bars: from flat, the previous Heikin-Ashi close moving above the Parabolic SAR with the HA close above its EMA 200 and its RSI 14 above 50 goes
long (mirrored for shorts); a stop at the distance to the 10-bar HA swing low; a profitable close while the HA close is back under the SAR closes.
Port of FMZ strategy #440797 "Parabolic Period and Bollinger Band Combined Moving Stop Loss Strategy" (HA_RSI).

FMZ source id: 440797

Source
    https://www.fmz.com/strategy/440797 (PineScript v5, FMZ last modified 2024-02-02 11:05:57).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 132-207), swing 10 / 10 (HA closes); EMA 200, RSI 14 on HA close; SAR 0.02 / 0.02 / 0.2; qty 0.5; slippage 25; date filter on (inTradeWindow is true)
    long = haClose > ema200(ha) and rsi(ha) > 50 and haClose[1] > sar and haClose[1] < sar[1] and flat -> entry, risk = (close - lowest(haClose, 10)) / close;  stop = avg price x (1 - risk)
    closeHA[1] < sar and close > avg price -> close long;  closeHA[1] > sar and close < avg price -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The Heikin-Ashi values come from the chart's own bars; the SAR is Pine's on the regular bars. The
      stop distance is set on the signal bar: sl_stop = risk, shifted one bar inside stops() and
      re-based on the fill (the script sends it from the fill bar on); a risk at or under zero puts the
      stop through the market and the trade exits at the fill bar. The SAR closes are bar tests against
      the fill price, sent at the next open. Entries only from flat. The date window is not applied
      (inTradeWindow is true). Opposite entries cannot occur (entries only from flat). Stop module:
      portfolio_kwargs {} (driver D4). Stops on 3-hour bars: mark coarse_bar_stop. The 0.5 quantity,
      capital and slippage are sizing and costs. FREQ = "3h" from the backtest header (bars on UTC
      multiples of 3 hours).

Admission criteria
    1 fits the interface: PASS, bar-close orders; stop fixed at entry from signal-bar data.
    2 generic: PASS, Heikin-Ashi close, SAR, EMA and RSI.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: quantity, capital and slippage settings.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur (entries only from flat).

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_440797_heikin_ashi_sar_flip_swing_stop"
FAMILY = "parabolic_sar"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "swing": [10, 20],
    "ema_v": [200, 100],
}
DEFAULT_PARAMS = {"swing": 10, "ema_v": 200, "rsi_v": 14, "start": 0.02, "inc": 0.02, "mx": 0.2}


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


def _sar(h, lo, c, start, inc, mx):
    """Pine's sar reference block: the SAR value (NaN on the first bar)."""
    n = len(c)
    out = np.full(n, np.nan)
    result = max_min = acc = np.nan
    below = False
    for i in range(1, n):
        first = False
        if i == 1:
            if c[1] > c[0]:
                below, max_min, result = True, h[1], lo[0]
            else:
                below, max_min, result = False, lo[1], h[0]
            first, acc = True, start
        result = result + acc * (max_min - result)
        if below:
            if result > lo[i]:
                first, below = True, False
                result, max_min, acc = max(h[i], max_min), lo[i], start
        else:
            if result < h[i]:
                first, below = True, True
                result, max_min, acc = min(lo[i], max_min), h[i], start
        if not first:
            if below:
                if h[i] > max_min:
                    max_min, acc = h[i], min(acc + inc, mx)
            else:
                if lo[i] < max_min:
                    max_min, acc = lo[i], min(acc + inc, mx)
        if below:
            result = min(result, lo[i - 1])
            if i > 1:
                result = min(result, lo[i - 2])
        else:
            result = max(result, h[i - 1])
            if i > 1:
                result = max(result, h[i - 2])
        out[i] = result
    return out


def _setup(bars_df, p):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    hac = (o + h + lo + c) / 4
    sar = pd.Series(_sar(h.to_numpy(dtype=float), lo.to_numpy(dtype=float), c.to_numpy(dtype=float),
                         float(p["start"]), float(p["inc"]), float(p["mx"])), index=c.index)
    ema = hac.ewm(span=int(p["ema_v"]), adjust=False).mean()
    r = _rsi(hac, int(p["rsi_v"]))
    h1 = hac.shift(1)
    lsig = (hac > ema) & (r > 50) & (h1 > sar) & (h1 < sar.shift(1))
    ssig = (hac < ema) & (r < 50) & (h1 < sar) & (h1 > sar.shift(1))
    n = int(p["swing"])
    risk_l = (c - hac.rolling(n).min()) / c
    risk_s = (hac.rolling(n).max() - c) / c
    risk = risk_l.where(lsig, risk_s.where(ssig))
    x_l = (h1 < sar).to_numpy()
    x_s = (h1 > sar).to_numpy()
    return lsig.to_numpy(), ssig.to_numpy(), risk, x_l, x_s


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    lsig, ssig, risk_s, x_l, x_s = _setup(bars_df, p)
    rk = risk_s.to_numpy()
    ov, cv = bars_df["open"].to_numpy(dtype=float), bars_df["close"].to_numpy(dtype=float)
    hv, lv = bars_df["high"].to_numpy(dtype=float), bars_df["low"].to_numpy(dtype=float)
    m = len(ov)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos, entry_i, s_ = 0, -1, np.nan
    for i in range(m):
        if pos != 0 and i >= entry_i and s_ > 0:
            x = ov[entry_i]
            if pos == 1 and lv[i] <= x * (1 - s_):
                pos = 0
            elif pos == -1 and hv[i] >= x * (1 + s_):
                pos = 0
        if pos != 0 and i >= entry_i:
            x = ov[entry_i]
            if (not s_ > 0 and i == entry_i) or (pos == 1 and x_l[i] and cv[i] > x) or (pos == -1 and x_s[i] and cv[i] < x):
                (lx if pos == 1 else sx)[i] = True
                pos = 0
                continue
        if pos == 0 and i + 1 < m and not np.isnan(rk[i]):
            if lsig[i]:
                le[i], pos, entry_i, s_ = True, 1, i + 1, rk[i]
            elif ssig[i]:
                se[i], pos, entry_i, s_ = True, -1, i + 1, rk[i]
    ix = bars_df.index
    return tuple(pd.Series(a, index=ix) for a in (le, lx, se, sx))


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    r = _setup(bars_df, p)[2]
    return {"sl_stop": r.where(r > 0).shift(1)}


def portfolio_kwargs(**params):
    return {}
