"""Stochastic 14 / 3 turns with volume 80 % above its SMA 20, or an EMA 14 / 23 golden cross, on green candles, hourly bars, long only, through the script's own bought state: a buy opens the long; a stochastic fall back under 20 after a middle-zone visit, the EMA death cross, a stochastic fall from overbought, or a close 6 % under the buy close closes it.
Port of FMZ strategy #430833 "Dual Pressure Quantitative Trading Strategy" (SW SVE - Stochastic+Vol+EMAs [Sergio Waldoke]).

FMZ source id: 430833

Source
    https://www.fmz.com/strategy/430833 (PineScript v3, FMZ last modified 2023-11-02 13:56:23).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 338-480), stoch 14 / 3 (80 / 20); EMA 14 / 23 / 40; volume SMA 20, +80 %; stop threshold 6 % of the buy close (close test); middle zone 35-80
    buy = (k, d <= 20, crossover(k, d), both rising, green, volume / sma >= 1.8) or (both rising, volume ok, green, crossover(k[1], d[1])) or (crossover(ema14, ema23), both rising, green);  buy and not already_bought -> entry buy
    sell = (k, d <= 20 and was_in_middle_zone) or crossunder(ema14, ema23) or (crossunder(k, d) from >= 80, both falling, k <= 80) or close < 0.94 x buy close;  sell and already_bought and not buy and (middle zone or stop) -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The script's already_bought / bought_price / was_in_middle_zone state runs as written, in source order
      (the middle zone is k and d above 35 = 1.75 x 20 and under 80). The stop is a close test against 94 %
      of the buy bar's close. The trend EMA 40 only feeds plots. Long only. The 100 % of equity size and
      commission are sizing / costs. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; close-based stop.
    2 generic: PASS, stochastic turns with volume confirmation and EMA crosses.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity, commission 0.25 % stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in volume / sma(volume, 20) >= 1.8; exchange volume to be compared later (Austin, 2026-10-23).
Session open: not used (the 2018 .. 2030 inputs are not used by the orders).
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_430833_stoch_volume_ema_cross_state_machine_long"
FAMILY = "stochastic_trend"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "volume_factor": [80.0, 40.0],
    "threshold_sl": [6.0, 3.0],
}
DEFAULT_PARAMS = {"volume_factor": 80.0, "threshold_sl": 6.0, "stoch_k": 14, "stoch_d": 3, "over_buying": 80.0,
                  "over_selling": 20.0, "fast_ema": 14, "slow_ema": 23, "volume_periods": 20}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c, v = (bars_df[k] for k in ("open", "high", "low", "close", "volume"))
    n = int(p["stoch_k"])
    k = 100 * (c - lo.rolling(n).min()) / (h.rolling(n).max() - lo.rolling(n).min()).replace(0.0, np.nan)
    d = k.rolling(int(p["stoch_d"])).mean()
    fe = c.ewm(span=int(p["fast_ema"]), adjust=False).mean()
    se_ = c.ewm(span=int(p["slow_ema"]), adjust=False).mean()
    vr = v / v.rolling(int(p["volume_periods"])).mean()
    vf = float(p["volume_factor"]) / 100 + 1
    ob, os_ = float(p["over_buying"]), float(p["over_selling"])
    grow = lambda x: x > x.shift(1)
    xkd = (k > d) & (k.shift(1) <= d.shift(1))
    ukd = (k < d) & (k.shift(1) >= d.shift(1))
    green = c > o
    b1 = (k <= os_) & (d <= os_) & xkd & grow(k) & grow(d) & green & (vr >= vf)
    b2 = grow(k) & grow(d) & (vr >= vf) & green & xkd.shift(1, fill_value=False)
    b3 = (fe > se_) & (fe.shift(1) <= se_.shift(1)) & grow(fe) & grow(se_) & green
    buy0 = (b1 | b2 | b3).to_numpy()
    s_low = ((k <= os_) & (d <= os_)).to_numpy()
    s_dx = ((fe < se_) & (fe.shift(1) >= se_.shift(1))).to_numpy()
    s_ob = (ukd & (k.shift(1) >= ob) & (d.shift(1) >= ob) & ~grow(k) & ~grow(d) & (k <= ob)).to_numpy()
    mid = ((k > os_ * 1.75) & (k < ob) & (d > os_ * 1.75) & (d < ob)).to_numpy()
    cv = c.to_numpy(dtype=float)
    stop_k = float(p["threshold_sl"]) / 100
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    wimz_p, ab_p, bp_p = False, False, 0.0
    for i in range(m):
        wimz = wimz_p or mid[i]                        # the k == d start value is overwritten, as written
        sell = (s_low[i] and wimz) or s_dx[i] or s_ob[i]
        ab = ab_p
        buy = buy0[i] and not ab
        wimz = (not buy and wimz) or mid[i]
        ab = ab_p or buy
        bp = cv[i] * (1 - stop_k) if buy else bp_p
        trig = cv[i] < bp
        sell = (sell or trig) and ab and not buy and (wimz or trig)
        ab = ab and not sell
        bp = 0.0 if sell else bp
        wimz = (not sell) and wimz
        le[i], lx[i] = buy, sell
        wimz_p, ab_p, bp_p = wimz, ab, bp
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
