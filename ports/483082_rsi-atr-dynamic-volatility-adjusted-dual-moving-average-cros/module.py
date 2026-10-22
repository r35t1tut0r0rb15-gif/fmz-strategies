"""SMA 9 / 21 crossings with RSI 14 under 70 / over 30 and an ATR 14 floor, hourly bars: the up-cross goes long and the down-cross goes short, each with a 0.5 % stop and a 1 % target from the fill; reversing.
Port of FMZ strategy #483082 "基于动态波动率调整的双均线交叉与RSI-ATR复合过滤交易系统-Dynamic-Volatility-Adjusted-Dual-Moving-Average-Crossover-System-with-RSI-ATR-Composite-Filter" (Simplified MA Crossover Strategy with Disable Options).

FMZ source id: 483082

Source
    https://www.fmz.com/strategy/483082 (PineScript v5, FMZ last modified 2025-02-21 11:58:43).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 94-158), SMA 9 / 21; RSI 14 / 70 / 30 filter on; ATR 14 over 0.005 filter on; stop 0.5 %; RR 2; risk 2 % sizing; 10 % of equity
    crossover(sma9, sma21) and rsi < 70 and atr > 0.005 -> entry Long + exit(limit = avg x 1.01, stop = avg x 0.995)
    crossunder(sma9, sma21) and rsi > 30 and atr > 0.005 -> entry Short + exit(limit = avg x 0.99, stop = avg x 1.005)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the ATR floor 0.005 is a price amount; read at the header's SOL_USDT prices (about
      200) as 0.005 / 200 = 2.5e-05 of the close (as #440456 reads price units).
    * The exit is sent on the signal bar, where position_avg_price is na from flat (or the other side's
      price in a reversal); it is ported as the 0.5 % / 1 % bracket around the fill, active from the fill
      bar (as #440797). The crossings alternate. An entry on the other side reverses (REVERSAL INTENDED).
      Stop module: portfolio_kwargs {} (driver D4). The risk-sized quantity and the 10 % of equity default
      are sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; percent bracket from the fill.
    2 generic: ADAPT, the ATR floor read as a fraction of the close at the header's prices.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: risk-sized quantity and 10 % of equity stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_483082_sma9_21_cross_rsi_atr_floor_0_5pct_rr2_bracket_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "stop_loss_perc": [0.5, 1.0],
    "risk_reward_ratio": [2.0, 3.0],
}
DEFAULT_PARAMS = {"stop_loss_perc": 0.5, "risk_reward_ratio": 2.0, "short_length": 9, "long_length": 21,
                  "rsi_length": 14, "rsi_ob": 70, "rsi_os": 30, "atr_length": 14, "min_atr_frac": 2.5e-05}


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
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    r = 100 - 100 / (1 + up / dn)
    r = r.where(dn != 0, 100.0).where(up != 0, 0.0)
    return r.where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    f = c.rolling(int(p["short_length"])).mean()
    s = c.rolling(int(p["long_length"])).mean()
    r = _rsi(c, int(p["rsi_length"]))
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]
    atr_ok = _rma(tr, int(p["atr_length"])) > float(p["min_atr_frac"]) * c
    le = (f > s) & (f.shift(1) <= s.shift(1)) & (r < float(p["rsi_ob"])) & atr_ok
    se = (f < s) & (f.shift(1) >= s.shift(1)) & (r > float(p["rsi_os"])) & atr_ok
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    idx = bars_df.index
    a = float(p["stop_loss_perc"]) / 100
    sl = pd.Series(a, index=idx).shift(1)
    tp = pd.Series(a * float(p["risk_reward_ratio"]), index=idx).shift(1)
    return {"sl_stop": sl, "tp_stop": tp}


def portfolio_kwargs(**params):
    return {}
