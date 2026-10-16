"""SAR trend + EMA 10 / SMA 17 cross + MACD + RSI(5) confluence with a 5 ATR bracket, 10-minute bars: from flat, a
SAR up-trend with EMA 10 crossing above SMA 17, a positive MACD histogram and RSI 5 above 72 goes long (mirror
short); the opposite confluence closes the position.
Port of FMZ strategy #429479 "Multifactor Dynamic Money Management Strategy" (EURUSD 1min strat RISK %%).

FMZ source id: 429479

Source
    https://www.fmz.com/strategy/429479 (PineScript v4, FMZ last modified 2023-10-17 15:09:59).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 217-417), RSI 5 (23 / 72), MACD 12 / 26 / 9 (SMAs), SAR 0.02 / 0.02 / 0.2, BB 17, EMA 10, ATR 14 x 5 / 5
    long = uptrend and crossover(ema10, sma17) and hist > 0 and rsi5 > 72; short = downtrend and crossunder and hist < 0 and rsi5 < 23
    flat -> entry on long / short (oca); exit(loss = stop, profit = target) with stop = target = atr x 100000 x 5 ticks
    shortCondition closes a long, longCondition closes a short; equity protector close_all when the open loss > 1 % of balance

Interpretation choices (Pine rules in SURVEY_README.md)
    * The SAR is the source's own loop (TradingView's reference parabolic SAR); its trend flag is used.
    * Criterion 2: the bracket is atr x 100000 x 5 ticks; on a 5-digit FX pair (the author's EURUSD) that is
      5 x ATR(14): sl_atr = tp_atr = 5 x Wilder ATR(14) of the signal bar, shifted one bar inside stops(),
      re-based on the fill.
    * Entries only from flat (`not is_open`): "flat" follows the house bracket on bars (the loop marks the
      position closed once a bar's high / low reaches the stop or target from the fill price), and the
      opposite confluence is a close signal. Opposite entries cannot occur.
    * The equity protector, the risk-% lot size and the session strings are money management / unused:
      stored, not ported. Stop module: portfolio_kwargs {} (driver D4). FREQ = "10min" from the header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: ADAPT, the FX tick bracket -> ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the risk-% sizing and the equity protector stored; the bracket quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_429479_sar_ema_macd_rsi_bracket"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "10min"  # backtest header period: 10m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_atr": [5.0, 2.0],
    "tp_atr": [5.0, 2.0],
}
DEFAULT_PARAMS = {"rsi_length": 5, "oversold": 23, "overbought": 72, "macd_fast": 12, "macd_slow": 26,
                  "macd_signal": 9, "sar_start": 0.02, "sar_inc": 0.02, "sar_max": 0.2, "bb_length": 17,
                  "ema_length": 10, "atr_length": 14, "sl_atr": 5.0, "tp_atr": 5.0}


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


def _rsi(x, n):
    d = x.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    r = 100 - 100 / (1 + up / dn)
    return r.where(dn != 0, 100.0).where(up.notna() & dn.notna())


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    return _rma(tr, n)


def _sar_trend(bars_df, start, inc, maximum):
    """The source's SAR loop (lines 257-323); returns its uptrend flag per bar (0 before bar 1)."""
    h, lo, c = (bars_df[k].to_numpy(dtype=float) for k in ("high", "low", "close"))
    m = len(c)
    out = np.zeros(m, dtype=np.int8)                    # 1 up, -1 down, 0 na
    up = None
    ep = nxt = np.nan
    af = start
    for i in range(1, m):
        first = False
        sar = nxt
        if i == 1:
            if c[1] > c[0]:
                up, ep, psar, pep = True, h[1], lo[0], h[1]
            else:
                up, ep, psar, pep = False, lo[1], h[0], lo[1]
            first = True
            sar = psar + start * (pep - psar)
        if up:
            if sar > lo[i]:
                first, up, sar, ep, af = True, False, max(ep, h[i]), lo[i], start
        else:
            if sar < h[i]:
                first, up, sar, ep, af = True, True, min(ep, lo[i]), h[i], start
        if not first:
            if up and h[i] > ep:
                ep, af = h[i], min(af + inc, maximum)
            elif (not up) and lo[i] < ep:
                ep, af = lo[i], min(af + inc, maximum)
        if up:
            sar = min(sar, lo[i - 1])
            if i > 1:
                sar = min(sar, lo[i - 2])
        else:
            sar = max(sar, h[i - 1])
            if i > 1:
                sar = max(sar, h[i - 2])
        nxt = sar + af * (ep - sar)
        out[i] = 1 if up else -1
    return out


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    trend = _sar_trend(bars_df, float(p["sar_start"]), float(p["sar_inc"]), float(p["sar_max"]))
    r = _rsi(c, int(p["rsi_length"]))
    macd = c.rolling(int(p["macd_fast"])).mean() - c.rolling(int(p["macd_slow"])).mean()
    hist = macd - macd.rolling(int(p["macd_signal"])).mean()
    ema = c.ewm(span=int(p["ema_length"]), adjust=False).mean()
    bb = c.rolling(int(p["bb_length"])).mean()
    xo = ((ema > bb) & (ema.shift(1) <= bb.shift(1))).to_numpy()
    xu = ((ema < bb) & (ema.shift(1) >= bb.shift(1))).to_numpy()
    long_c = (trend == 1) & xo & (hist > 0).to_numpy() & (r > p["overbought"]).to_numpy()
    short_c = (trend == -1) & xu & (hist < 0).to_numpy() & (r < p["oversold"]).to_numpy()
    frac = (_atr(bars_df, int(p["atr_length"])) / c).to_numpy()
    ov, hv, lv = o.to_numpy(dtype=float), h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    m = len(ov)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, entry_i, sl, tp = 0, -1, np.nan, np.nan
    for i in range(m):
        if pos != 0 and i >= entry_i:                    # house bracket from the fill price
            e = ov[entry_i]
            if pos == 1 and (lv[i] <= e * (1 - sl) or hv[i] >= e * (1 + tp)):
                pos = 0
            elif pos == -1 and (hv[i] >= e * (1 + sl) or lv[i] <= e * (1 - tp)):
                pos = 0
        if pos == 0:
            if long_c[i] and not np.isnan(frac[i]):
                le[i], pos, entry_i = True, 1, i + 1
                sl, tp = p["sl_atr"] * frac[i], p["tp_atr"] * frac[i]
            elif short_c[i] and not np.isnan(frac[i]):
                se[i], pos, entry_i = True, -1, i + 1
                sl, tp = p["sl_atr"] * frac[i], p["tp_atr"] * frac[i]
        elif pos == 1 and short_c[i]:
            lx[i], pos = True, 0
        elif pos == -1 and long_c[i]:
            sx[i], pos = True, 0
    idx = bars_df.index
    return (pd.Series(le, index=idx), pd.Series(lx, index=idx), pd.Series(se, index=idx),
            pd.Series(sx, index=idx))


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    frac = _atr(bars_df, int(p["atr_length"])) / bars_df["close"]
    return {"sl_stop": (p["sl_atr"] * frac).shift(1), "tp_stop": (p["tp_atr"] * frac).shift(1)}


def portfolio_kwargs(**params):
    return {}
