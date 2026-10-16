"""RSI 40 / 60 pullbacks in the EMA 100 trend, 5-minute bars, from flat: above the EMA 100 an RSI 14 under 40 goes long,
below it an RSI over 60 goes short; each position has a 1 % target and a 1.5 % stop from the entry price.
Port of FMZ strategy #430760 "基于RSI指标的短线反转交易策略RSI-Mean-Reversion-Trading-Strategy" (RSI Strategy (Sarahann999)).

FMZ source id: 430760

Source
    https://www.fmz.com/strategy/430760 (PineScript v5, FMZ last modified 2023-11-01 16:15:30).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 165-220), EMA 100, RSI 14, 40 / 60, TP 1 %, SL 1.5 %
    close > ema100 and rsi < 40 and flat -> entry long;  close < ema100 and rsi > 60 and flat -> entry short
    long: exit(limit = avg x 1.01, stop = avg x 0.985);  short: exit(limit = avg x 0.99, stop = avg x 1.015)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is a fixed fraction of the average price (the fill): tp 0.01, sl 0.015.
    * Entries only from flat: "flat" follows the house bracket on bars. Opposite entries cannot occur.
      Stop module: portfolio_kwargs {} (driver D4). FREQ = "5min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; a fixed percentage bracket.
    2 generic: PASS, RSI levels, an EMA and percentage exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code; the bracket quoted in original_sizing.txt.
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

NAME = "fmz_430760_rsi_40_60_trend_bracket"
FAMILY = "rsi_oscillator"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "ema_len": [100, 200],
    "tp_pct": [1.0, 2.0],
}
DEFAULT_PARAMS = {"ema_len": 100, "rsi_len": 14, "os": 40, "ob": 60, "tp_pct": 1.0, "sl_pct": 1.5}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _rsi(c, n):
    ch = c.diff()
    up = ch.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-ch.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    rsi = 100 - 100 / (1 + up / dn)
    rsi = rsi.where(up != 0, 0.0)
    return rsi.where(dn != 0, 100.0).where(ch.notna())


def _run(bars_df, p):
    c = bars_df["close"]
    ema = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    r = _rsi(c, int(p["rsi_len"]))
    buy = ((c > ema) & (r < p["os"])).to_numpy()
    sell = ((c < ema) & (r > p["ob"])).to_numpy()
    s_, t_ = float(p["sl_pct"]) / 100, float(p["tp_pct"]) / 100
    ov, hv, lv = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "low"))
    m = len(ov)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, entry_i = 0, -1
    for i in range(m):
        if pos != 0 and i >= entry_i:                    # house bracket from the fill price
            e = ov[entry_i]
            if pos == 1 and (lv[i] <= e * (1 - s_) or hv[i] >= e * (1 + t_)):
                pos = 0
            elif pos == -1 and (hv[i] >= e * (1 + s_) or lv[i] <= e * (1 - t_)):
                pos = 0
        if pos == 0 and buy[i]:
            le[i], pos, entry_i = True, 1, i + 1
        elif pos == 0 and sell[i]:
            se[i], pos, entry_i = True, -1, i + 1
    return le, se


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se = _run(bars_df, p)
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), false, pd.Series(se, index=idx), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_pct"]) / 100, "tp_stop": float(p["tp_pct"]) / 100}


def portfolio_kwargs(**params):
    return {}
