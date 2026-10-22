"""Bollinger and stochastic-RSI reversals, 2-hour bars: from flat, an up close below the band basis minus half a deviation with the stochastic RSI K under 30 goes long, the mirrored down close short;
a long closes on a down close over the basis plus half a deviation with K over 70 once 1 % up, or on a close one ATR(10) under its best close step; shorts mirrored (as written).
Port of FMZ strategy #440467 "Trend Following Strategy Based on Multiple Indicators" (Dragon Bot - Default Script).

FMZ source id: 440467

Source
    https://www.fmz.com/strategy/440467 (PineScript v3, FMZ last modified 2024-01-30 17:51:04).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 173-536), profit 1 %; shorts on, flipping off, stop off; trailing on with ATR (10) x 1; BB 20 / 2 (0.5 / 0.5); stoch RSI 3 / 3 / 14 / 14 (30 / 70); added ATR / OC2 off
    makelong (flat) = close < basis - 0.5 dev and krsi < 30 and close > close[1];  makeshort (flat) = close > basis + 0.5 dev and krsi > 70 and close < close[1];  buyprice = scaler = close
    long: scaler := close when close > scaler + atr10;  closelong = (close > buyprice x 1.01 and close > basis + 0.5 dev and krsi > 70 and close < close[1]) or close < scaler - atr10;  shorts: the profit exit tests close < basis + 0.5 dev and krsi < 70 with close > close[1], as written

Interpretation choices (Pine rules in SURVEY_README.md)
    * The script's own longs / shorts flags track the position (entries only from flat, flipping off),
      and every exit is a bar-close test sent at the next open. The short profit exit uses the sell band
      and the 70 level as written. The "profit" security call is the chart's own close. The date and
      test-period switches are off. Pine's stdev is the population deviation. Opposite entries cannot
      occur (entries only from flat). No sizing code. FREQ = "2h" from the backtest header (bars on UTC
      multiples of 2 hours).

Admission criteria
    1 fits the interface: PASS, bar-close orders; close-tested exits.
    2 generic: PASS, Bollinger levels, stochastic RSI and an ATR step trail.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG440467 (2 members, best partner #440993, Jaccard 0.974); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur (entries only from flat).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_440467_dragon_bot_bb_stochrsi_atr_step"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "sellprofit": [1.0, 3.0],
    "atr_multi": [1.0, 2.0],
}
DEFAULT_PARAMS = {"sellprofit": 1.0, "atr_multi": 1.0, "trail_atr_len": 10, "bb_len": 20, "bb_mult": 2.0,
                  "bb_buy": 0.5, "bb_sell": 0.5, "smooth_k": 3, "rsi_len": 14, "stoch_len": 14,
                  "buy_rsi": 30, "sell_rsi": 70}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    tatr = (_rma(tr, int(p["trail_atr_len"])) * float(p["atr_multi"])).to_numpy()
    r = _rsi(c, int(p["rsi_len"]))
    sn = int(p["stoch_len"])
    ll, hh = r.rolling(sn).min(), r.rolling(sn).max()
    krsi = (100.0 * (r - ll) / (hh - ll).where(hh > ll)).rolling(int(p["smooth_k"])).mean()
    bl = int(p["bb_len"])
    basis = c.rolling(bl).mean()
    dev = float(p["bb_mult"]) * c.rolling(bl).std(ddof=0)
    bbbuy = basis - dev * float(p["bb_buy"])
    bbsell = basis + dev * float(p["bb_sell"])
    up, dn = (c > pc).to_numpy(), (c < pc).to_numpy()
    k = krsi.to_numpy()
    b_lo, b_hi = (c < bbbuy).to_numpy(), (c > bbsell).to_numpy()
    b_lo_s = (c < bbsell).to_numpy()
    cv = c.to_numpy(dtype=float)
    br, sr = float(p["buy_rsi"]), float(p["sell_rsi"])
    pf = float(p["sellprofit"]) / 100
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    longs = shorts = 0
    buyprice = scaler = np.nan
    for i in range(m):
        if longs < 1 and shorts < 1 and b_lo[i] and k[i] < br and up[i]:
            buyprice = scaler = cv[i]
            longs, shorts = 1, 0
        elif shorts < 1 and longs < 1 and b_hi[i] and k[i] > sr and dn[i]:
            buyprice = scaler = cv[i]
            shorts, longs = 1, 0
        if longs > 0 and cv[i] > scaler + tatr[i]:
            scaler = cv[i]
        if shorts > 0 and cv[i] < scaler - tatr[i]:
            scaler = cv[i]
        if longs > 0:
            pex = buyprice * (1 + pf) < cv[i] and b_hi[i] and k[i] > sr and dn[i]
            if pex or cv[i] < scaler - tatr[i]:
                longs = 0
        if shorts > 0:
            pex = buyprice * (1 - pf) > cv[i] and b_lo_s[i] and k[i] < sr and up[i]
            if pex or cv[i] > scaler + tatr[i]:
                shorts = 0
        tgt[i] = 1 if longs > 0 else (-1 if shorts > 0 else 0)
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), pd.Series((prev == 1) & (tgt != 1), index=ix),
            pd.Series((tgt == -1) & (prev != -1), index=ix), pd.Series((prev == -1) & (tgt != -1), index=ix))


def portfolio_kwargs(**params):
    return {}
