"""Heikin-Ashi SuperTrend pullbacks with a CCI trailing line, 4-hour bars: a flat-bottomed HA candle pulling back to its HMA 15 / EMA 20, with the HA close near or above the HA SuperTrend (ATR 4 x 2) and
the close above the previous CCI line, goes long; the mirror (RSI under 55) short; the close crossing the CCI line, or the first bar from 15:00 UTC, closes; reversing.
Port of FMZ strategy #441178 "基于Heikin-Ashi的超级趋势-trailing-stop损策略SuperTrend-Trailing-Stop-Strategy-Based-on-Heikin-Ashi" (sa-strategy with HTF-TSL).

FMZ source id: 441178

Source
    https://www.fmz.com/strategy/441178 (PineScript v4, FMZ last modified 2024-02-06 14:43:14).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 126-296), SuperTrend ATR 4 x 2 on HA closes; CCI line 20, ATR 5 x 1; HTF "240" = the chart's own 4h; exit hour 15, minute 15
    CCI line x: bufferDn = high + sma(tr, 5), bufferUp = low - sma(tr, 5), swapped on CCI zero crosses and ratcheted;  x = cci >= 0 ? bufferUp : cci <= 0 ? bufferDn : x[1];  htfx = security("240", x[1], lookahead_on)
    HA SuperTrend: TrendUp / TrendDown ratchet on haClose[1];  Trend = haClose > TrendDown[1] ? 1 : haClose < TrendUp[1] ? -1 : Trend[1];  crossup / crossdn = HA close crossing (now, 1 or 2 bars back) or beyond the line
    buy = haOpen == haLow and closeup and crossup and close > htfx;  sell = haOpen == haHigh and closedown and rsi(14) < 55 and crossdn and close < htfx;  rg / nm latches -> entry long / short on the first bar of a new state
    cross(close, x) or MarketClose -> close short, close long;  MarketClose = the first bar with hour >= 15 (minute test always true on 4h bars)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "240" security asks for the chart's own timeframe, so htfx is the CCI line one bar back; the
      heikinashi securities use the chart's own bars (HA built from the module's bars). The CCI line and the
      SuperTrend are ported as written (previous-bar values, nz starts). hour and minute are read on the UTC
      bar open: on 4-hour bars the 16:00 bar is the first with hour >= 15, so every position open then is
      closed at the next open. A close acts only on the held position; a close written after a reversing
      entry leaves the reversal standing (as #438020). REVERSAL INTENDED. No sizing code. FREQ = "4h" from
      the backtest header (bars on UTC multiples of 4 hours).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Heikin-Ashi SuperTrend, CCI line and time exit.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: daily close on the first 4-hour bar opening at or after 15:00 UTC (bar open time).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_441178_ha_supertrend_pullback_cci_line_reversal"
FAMILY = "supertrend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "pd": [4, 10],
    "factor": [2.0, 3.0],
}
DEFAULT_PARAMS = {"pd": 4, "factor": 2.0, "cci_len": 20, "atr_len": 5, "multiplier": 1.0, "exit_hour": 15}


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


def _wma(x, n):
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda a: np.dot(a, w) / w.sum(), raw=True)


def _hma(src, n):
    return _wma(2 * _wma(src, n // 2) - _wma(src, n), int(round(np.sqrt(n))))


def _cci(x, n):
    ma = x.rolling(n).mean()
    md = x.rolling(n).apply(lambda a: np.abs(a - a.mean()).mean(), raw=True)
    return (x - ma) / (0.015 * md)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = bars_df["open"], bars_df["high"], bars_df["low"], bars_df["close"]
    ov, hv, lv, cv = (s.to_numpy(dtype=float) for s in (o, h, lo, c))
    m = len(cv)
    hac = (ov + hv + lv + cv) / 4
    hao = np.empty(m)
    for i in range(m):
        hao[i] = (ov[i] + cv[i]) / 2 if i == 0 else (hao[i - 1] + hac[i - 1]) / 2
    hah = np.maximum(hv, np.maximum(hao, hac))
    hal = np.minimum(lv, np.minimum(hao, hac))
    pc = c.shift(1)
    tr_na = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1).where(pc.notna())
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    # CCI trailing line (tempx)
    cci = _cci(c, int(p["cci_len"])).to_numpy()
    lcci = np.concatenate(([0.0], np.nan_to_num(cci[:-1], nan=0.0)))
    band = (float(p["multiplier"]) * tr_na.rolling(int(p["atr_len"])).mean()).to_numpy()
    tx = np.full(m, np.nan)
    pu = pdn = xp = np.nan
    for i in range(m):
        bd, bu = hv[i] + band[i], lv[i] - band[i]
        if cci[i] >= 0 and lcci[i] < 0:
            bu = pdn
        if cci[i] <= 0 and lcci[i] > 0:
            bd = pu
        if cci[i] >= 0:
            if bu < pu:
                bu = pu
        elif cci[i] <= 0:
            if bd > pdn:
                bd = pdn
        x = bu if cci[i] >= 0 else (bd if cci[i] <= 0 else xp)
        tx[i] = x
        pu, pdn, xp = bu, bd, x
    htfx = np.concatenate(([np.nan], tx[:-1]))
    # Heikin-Ashi SuperTrend
    atr = _rma(tr, int(p["pd"])).to_numpy()
    hl2 = (hv + lv) / 2
    fac = float(p["factor"])
    tsl = np.full(m, np.nan)
    tu = tdn = np.nan
    trd = 1
    for i in range(m):
        up_b, dn_b = hl2[i] - fac * atr[i], hl2[i] + fac * atr[i]
        hc1 = hac[i - 1] if i > 0 else np.nan
        ntu = (np.nan if np.isnan(up_b) else max(up_b, tu)) if hc1 > tu else up_b
        ntd = (np.nan if np.isnan(dn_b) else min(dn_b, tdn)) if hc1 < tdn else dn_b
        trd = 1 if hac[i] > tdn else (-1 if hac[i] < tu else trd)
        tsl[i] = ntu if trd == 1 else ntd
        tu, tdn = ntu, ntd
    hc = pd.Series(hac, index=c.index)
    ts = pd.Series(tsl, index=c.index)
    ts1 = ts.shift(1)
    crossup = ((hc > ts) & (hc.shift(1) <= ts1)) | ((hc.shift(1) > ts) & (hc.shift(2) <= ts1)) \
        | ((hc.shift(2) > ts) & (hc.shift(3) <= ts1)) | (hc > ts)
    crossdn = ((hc < ts) & (hc.shift(1) >= ts1)) | ((hc.shift(1) < ts) & (hc.shift(2) >= ts1)) \
        | ((hc.shift(2) < ts) & (hc.shift(3) >= ts1)) | (hc < ts)
    hm, e20 = _hma(hc, 15), hc.ewm(span=20, adjust=False).mean()
    hh_, hl_ = pd.Series(hah, index=c.index), pd.Series(hal, index=c.index)
    closedown = ((hc < hm) & (hh_ > hm)) | ((hc < e20) & (hh_ > e20))
    closeup = ((hc > hm) & (hl_ < hm)) | ((hc > e20) & (hl_ < e20))
    hx = pd.Series(htfx, index=c.index)
    ho = pd.Series(hao, index=c.index)
    buy = ((ho == hl_) & closeup & crossup & (c > hx)).to_numpy()
    sell = ((ho == hh_) & closedown & (_rsi(c, 14) < 55) & crossdn & (c < hx)).to_numpy()
    txs = pd.Series(tx, index=c.index)
    xc = (((c > txs) & (pc <= txs.shift(1))) | ((c < txs) & (pc >= txs.shift(1)))).to_numpy()
    hr = bars_df.index.tz_convert("UTC").hour
    et = pd.Series(hr >= int(p["exit_hour"]), index=c.index)
    mc = (et & ~et.shift(1, fill_value=False)).to_numpy()
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    rg = nm = 0
    held = 0
    for i in range(m):
        rg_p, nm_p = rg, nm
        rg = 1 if buy[i] else (2 if xc[i] else rg)
        nm = 1 if sell[i] else (2 if xc[i] else nm)
        new = held
        if i > 0 and rg != rg_p and rg == 1 and new != 1:
            new = 1
        if i > 0 and nm != nm_p and nm == 1 and new != -1:
            new = -1
        if (xc[i] or mc[i]) and held == -1 and new == -1:
            new = 0
        if (xc[i] or mc[i]) and held == 1 and new == 1:
            new = 0
        if new != held and i + 1 < m:
            if new == 1:
                le[i] = True
            elif new == -1:
                se[i] = True
            elif held == 1:
                lx[i] = True
            else:
                sx[i] = True
            held = new
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
