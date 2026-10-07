"""Big Snapper (SuperTrend filter) signal buffered until a Chaikin-volatility burst on the right
side of EMA55 and a candle of the right colour; exits on an RSI(11) retreat from overbought
(oversold), on the opposite setup, or on a close-based swing stop (long side only, as written).
Port of FMZ strategy #362055 "Big-Snapper-Alerts-R30-Chaiking-Volatility-condition-TP-RSI".

Source
    https://www.fmz.com/strategy/362055 (PineScript v5, FMZ last modified 2022-05-09 21:37:30).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 175-568; filterOption "SuperTrend" default)
    ma_coloured = HMA(close,18); clrdirection = rising/falling(ma_coloured, 2)
    STrend: hl2 -/+ 3.618*ATR(5) ratchet; stbuy counts bars of clrdirection==1 and STrend==1
    long = stbuy == 1 -> longbuffer = 1;  triggerlong = close > EMA(close,55)
    longe = longbuffer and triggerlong and ROC(EMA(high-low,10),12) > 3.5
    longe and close > open -> up = 1, SLup = close - 0.7*(high-low)
    closelong = (RSI11 was > 70 and is now < 63.8) or shorte (previous bar) or low < SLup
    entry long while up; close long on closelong      (short side mirror, without the SL)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Every flag is reproduced in script order; persistent `var` state carries across bars.
      `SL` is set only from the long side's SLup (the short side never sets SLdown into SL), as
      written; the stop is a close-time test of the bar's low -> exit signal (rule 3 analogy).
    * Orders on one bar: the close commands act on the position held at the bar's start; a fresh
      `up` on the same bar re-opens (net: stays long). Entries reverse an opposite position:
      REVERSAL INTENDED (portfolio_kwargs {}).
    * The ROC of the EMA of the bar range is a percentage: criterion 2 PASS.
    * FREQ = "2h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_362055_snapper_supertrend_chaikin_rsi"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-07, user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "st_factor": [2.5, 3.618],
    "st_len": [5, 10],
    "len_coloured": [12, 18, 24],
}
DEFAULT_PARAMS = {"st_factor": 3.618, "st_len": 5, "len_coloured": 18, "len_medium": 55,
                  "chaikin_len": 10, "roc_len": 12, "chaikin_min": 3.5, "rsi_len": 11,
                  "overbought": 70, "oversold": 30, "ob_exit": 63.8, "os_exit": 36.2}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _rma(x, n):
    """Wilder smoothing as TA-Lib: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def _rsi(close, n):
    d = close.diff()
    return 100.0 - 100.0 / (1.0 + _rma(d.clip(lower=0), n) / _rma((-d).clip(lower=0), n))


def _atr_pine(bars, n):
    """ta.atr: Wilder RMA of the true range; the first bar's range is high - low (ta.tr(true))."""
    prev_close = bars["close"].shift(1)
    tr = pd.concat([bars["high"] - bars["low"],
                    (bars["high"] - prev_close).abs(),
                    (bars["low"] - prev_close).abs()], axis=1).max(axis=1)
    return _rma(tr, n)


def _wma(x, n):
    """ta.wma: linearly weighted MA, weight n on the current bar."""
    n = int(n)
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda a: np.dot(a, w) / w.sum(), raw=True)


def _hma(x, n):
    return _wma(2 * _wma(x, int(n / 2)) - _wma(x, n), int(round(np.sqrt(n))))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    mac = _hma(c, int(p["len_coloured"]))
    rising = (mac > mac.shift(1)) & (mac > mac.shift(2))
    falling = (mac < mac.shift(1)) & (mac < mac.shift(2))
    ema_m = c.ewm(span=int(p["len_medium"]), adjust=False).mean().to_numpy()
    rng_ema = (h - lo).ewm(span=int(p["chaikin_len"]), adjust=False).mean()
    k = int(p["roc_len"])
    xroc = (100 * (rng_ema - rng_ema.shift(k)) / rng_ema.shift(k)).to_numpy()
    rsi = _rsi(c, int(p["rsi_len"])).to_numpy()
    atr = _atr_pine(bars_df, int(p["st_len"])).to_numpy()
    hl2 = ((h + lo) / 2).to_numpy()
    rise, fall = rising.to_numpy(), falling.to_numpy()
    O, H, L, C = (s.to_numpy(dtype=float) for s in (o, h, lo, c))

    m = len(C)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    clr, st_up, st_dn, strend = 1, np.nan, np.nan, 1
    stbuy = stsell = 0
    up = down = 0
    longe = shorte = False
    sl = 0
    ev_up, sl_up = 0.0, 0.0
    lbuf = sbuf = 0
    t_ob = t_os = 0
    trig_l = trig_s = 0
    pos = 0
    for i in range(m):
        clr = 1 if rise[i] else (-1 if fall[i] else clr)
        sup, sdn = hl2[i] - p["st_factor"] * atr[i], hl2[i] + p["st_factor"] * atr[i]
        prev_up, prev_dn = st_up, st_dn
        st_up = max(sup, prev_up) if (i > 0 and C[i - 1] > prev_up) else sup
        st_dn = min(sdn, prev_dn) if (i > 0 and C[i - 1] < prev_dn) else sdn
        strend = 1 if C[i] > prev_dn else (-1 if C[i] < prev_up else strend)
        stbuy = stbuy + 1 if (clr == 1 and strend == 1) else 0
        stsell = stsell + 1 if (clr == -1 and strend == -1) else 0
        if np.isnan(atr[i]) or np.isnan(rsi[i]):
            continue
        if rsi[i] > p["overbought"]:
            t_ob = 1
        if rsi[i] < p["oversold"]:
            t_os = 1
        if ev_up > 0 and L[i] < sl_up:
            sl = 1
        close_long = (t_ob == 1 and rsi[i] < p["ob_exit"]) or shorte or sl == 1
        close_short = (t_os == 1 and rsi[i] > p["os_exit"]) or longe or sl == 1
        if close_long:
            up, longe, t_ob, trig_l, sl, ev_up = 0, False, 0, 0, 0, 0.0
        if close_short:
            down, shorte, t_os, trig_s, sl = 0, False, 0, 0, 0
        if C[i] < ema_m[i]:
            trig_l, trig_s = 0, 1
        if C[i] > ema_m[i]:
            trig_s, trig_l = 0, 1
        if stbuy == 1:
            lbuf = 1
        if stsell == 1:
            sbuf = 1
        burst = xroc[i] > p["chaikin_min"]
        longe = bool(lbuf and trig_l and burst)
        shorte = bool(sbuf and trig_s and burst)
        if longe and C[i] > O[i]:
            up, down, ev_up, sl_up, lbuf = 1, 0, C[i], C[i] - 0.7 * (H[i] - L[i]), 0
        if shorte and C[i] < O[i]:
            down, up, sl_up, sbuf = 1, 0, 0.0, 0
        new = pos
        if close_long and pos == 1:
            new = 0
        if close_short and pos == -1:
            new = 0
        if up:
            new = 1
        if down:
            new = -1
        if new != pos:
            if new == 1:
                le[i] = True
            elif new == -1:
                se[i] = True
            elif pos == 1:
                lx[i] = True
            else:
                sx[i] = True
            pos = new

    idx = bars_df.index
    return (pd.Series(le, index=idx), pd.Series(lx, index=idx),
            pd.Series(se, index=idx), pd.Series(sx, index=idx))


def portfolio_kwargs(**params):
    return {}
