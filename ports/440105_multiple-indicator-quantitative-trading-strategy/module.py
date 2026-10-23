"""Hourly bars: the first bar on which eight conditions agree (close above the session VWAP and the VWMA 20, EMA 10 > EMA 20, the ATR 22 x 5 trend up, RSI 14 above 56, EMA 9 > EMA 26, ADX 14 above 25, volume above its EMA 10) goes long; the first bar of the mirror goes short; each with a 0.5 % stop and a 1.5 % target from the signal close; reversing.
Port of FMZ strategy #440105 "Multiple Indicator Quantitative Trading Strategy" (Pinku Buy).

FMZ source id: 440105

Source
    https://www.fmz.com/strategy/440105 (PineScript v5, FMZ last modified 2024-01-26 16:19:47).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 190-495), EMA 10 / 20; vwap(hlc3); VWMA 20; trend ATR 22 x 5 on hl2; RSI 14, 44 / 56; EMA 9 / 26; ADX 14 / 14 > 25; volume EMA 10; multiple_signals on; SL 0.5 %, TP 1.5 %; averaging on (qty 1)
    g = buy_1 and buy_2 and buy_4 and trend == 1 and buy_5 and buy_6 and signal and signal_2;  buy = g and not g[1] -> entry buy (qty qn), exit(limit = longPrice x 1.015, stop = longPrice x 0.995)
    r mirror (sell_4 = close < ema2) -> entry sell, exit(limit = shortPrice x 0.985, stop = shortPrice x 1.005);  close buy when longTPhit or sell or longSLhit;  close sell likewise

Interpretation choices (Pine rules in SURVEY_README.md)
    * With averaging on, qn is reset to 1 every bar, so the doubling never applies (qty 1 is sizing).
      The bracket is sent on the signal bar from the close of the bar that opened the script's own
      long / short state (valuewhen(long_last, close)); a repeated signal in the same state re-sends the
      same levels, so the port fixes them at the opening signal's close, as fractions of the fill (exact;
      a level the fill has passed is taken at once, 1e-6 floor). The bar-close TP / SL closes test the
      same levels as the bracket, which fills first. The opposite signal reverses (the close on that
      bar acts on a position its entry changes). The trend is the classic ATR trend line (up / down
      bands ratcheted on the previous close). ADX by the script's dirmov (fixnan DI). REVERSAL INTENDED.
      Stop module: portfolio_kwargs {} (driver D4). FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket at the signal close as fractions of the fill.
    2 generic: PASS, eight-condition trend agreement edges.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: qty = qn (1 with averaging on), not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the session VWAP, the VWMA 20 and the volume > EMA 10 test; exchange volume to be compared later (Austin, 2026-10-23).
Session open: session VWAP anchored at the broker day (17:00 America/New_York).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_440105_eight_condition_agreement_edge_pct_bracket_1h_reversal"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "stop": [0.005, 0.01],
    "profit": [0.015, 0.03],
}
DEFAULT_PARAMS = {"len1": 10, "len2": 20, "vwma_len": 20, "str_period": 22, "str_mult": 5.0, "rsi_len": 14,
                  "over_sold": 44.0, "over_bought": 56.0, "ema_a": 26, "ema_b": 9, "adx_len": 14, "di_len": 14,
                  "adx_min": 25.0, "vol_ema": 10, "stop": 0.005, "profit": 0.015}


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


def _fixnan(x):
    """Pine fixnan: the last non-NaN value, NaN before the first."""
    v = x.to_numpy(dtype=float)
    idx = np.where(~np.isnan(v), np.arange(len(v)), 0)
    idx = np.maximum.accumulate(idx)
    return pd.Series(v[idx], index=x.index)


def _signals(bars_df, p):
    h, lo, c, v = (bars_df[k] for k in ("high", "low", "close", "volume"))
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1).where(pc.notna())
    day = broker_day(c.index)
    hlc3 = (h + lo + c) / 3
    cv = v.groupby(day).cumsum()
    vwap = (hlc3 * v).groupby(day).cumsum() / cv.where(cv != 0)
    sv = v.rolling(int(p["vwma_len"])).mean()
    vwma = (c * v).rolling(int(p["vwma_len"])).mean() / sv.where(sv != 0)
    e1 = c.ewm(span=int(p["len1"]), adjust=False).mean()
    e2 = c.ewm(span=int(p["len2"]), adjust=False).mean()
    atr = _rma(tr, int(p["str_period"])).to_numpy()
    src = ((h + lo) / 2).to_numpy()
    cvv = c.to_numpy(dtype=float)
    mult = float(p["str_mult"])
    m = len(cvv)
    trend = np.ones(m, dtype=np.int8)
    up_prev = dn_prev = np.nan
    t = 1
    for i in range(m):
        up = src[i] - mult * atr[i]
        dn = src[i] + mult * atr[i]
        up1 = up if np.isnan(up_prev) else up_prev
        dn1 = dn if np.isnan(dn_prev) else dn_prev
        if i > 0 and cvv[i - 1] > up1:
            up = max(up, up1)
        if i > 0 and cvv[i - 1] < dn1:
            dn = min(dn, dn1)
        if t == -1 and cvv[i] > dn1:
            t = 1
        elif t == 1 and cvv[i] < up1:
            t = -1
        trend[i] = t
        up_prev, dn_prev = up, dn
    rs = _rsi(c, int(p["rsi_len"]))
    ea = c.ewm(span=int(p["ema_a"]), adjust=False).mean()
    eb = c.ewm(span=int(p["ema_b"]), adjust=False).mean()
    upm, dnm = h.diff(), -lo.diff()
    plus_dm = pd.Series(np.where((upm > dnm) & (upm > 0), upm, 0.0), index=c.index).where(upm.notna())
    minus_dm = pd.Series(np.where((dnm > upm) & (dnm > 0), dnm, 0.0), index=c.index).where(dnm.notna())
    dl = int(p["di_len"])
    trr = _rma(tr, dl)
    plus = _fixnan(100 * _rma(plus_dm, dl) / trr)
    minus = _fixnan(100 * _rma(minus_dm, dl) / trr)
    s = plus + minus
    adx = 100 * _rma((plus - minus).abs() / s.where(s != 0, 1.0), int(p["adx_len"]))
    strong = adx > float(p["adx_min"])
    vol_ok = v > v.ewm(span=int(p["vol_ema"]), adjust=False).mean()
    tr_up = pd.Series(trend == 1, index=c.index)
    tr_dn = pd.Series(trend == -1, index=c.index)
    g = ((c > vwap) & (c > vwma) & (e1 > e2) & tr_up & (rs > float(p["over_bought"])) & (eb > ea) & strong & vol_ok)
    r = ((c < vwap) & (c < vwma) & (c < e2) & tr_dn & (rs < float(p["over_sold"])) & (eb < ea) & strong & vol_ok)
    buy = g & ~g.shift(1, fill_value=False)
    sell = r & ~r.shift(1, fill_value=False)
    return buy.to_numpy(), sell.to_numpy()


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    buy, sell = _signals(bars_df, p)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(buy & ~sell, index=ix), false, pd.Series(sell, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx, se, sx = simulate(bars_df, **params)
    o, c = bars_df["open"], bars_df["close"]
    k = c.shift(1) / o                                  # the signal close as a fraction of the fill
    st, pr = float(p["stop"]), float(p["profit"])
    lf, sf = le.shift(1, fill_value=False), se.shift(1, fill_value=False)
    sl_f = pd.Series(np.nan, index=o.index).mask(lf, 1 - k * (1 - st)).mask(sf, k * (1 + st) - 1)
    tp_f = pd.Series(np.nan, index=o.index).mask(lf, k * (1 + pr) - 1).mask(sf, 1 - k * (1 - pr))
    return {"sl_stop": sl_f.clip(lower=1e-6), "tp_stop": tp_f.clip(lower=1e-6)}


def portfolio_kwargs(**params):
    return {}
