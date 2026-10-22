""""Parallel" candle pairs, 2-hour bars, long only (side "Long"), entries only from flat: a big green candle after a big red one (bodies over 80 % of ranges larger than their 14-bar average) buys, with a target 3 R over the fill, R being the signal close minus (10-bar low - ATR 14); an RSI 14 of highs over 75 closes it. Its ratchet stop on the 10-bar low - ATR is not ported (pending).
Port of FMZ strategy #474670 "Advanced Dynamic Trailing Stop with Risk Reward Targeting Strategy" (Trailing stop 1).

FMZ source id: 474670

Source
    https://www.fmz.com/strategy/474670 (PineScript v5, FMZ last modified 2024-12-11 14:57:09).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 101-183), bar lookback 10; ATR 14 x 1.0; risk-reward 3; side Long; RSI exit on (75 / 25); size = 1000 / R
    bigred[1] and biggreen and atr ready and flat -> R := close - (lowest(low, 10) - atr), entry Long (qty 1000 / R);  long: trail := max(trail, lowest(low, 10) - atr) every bar;  exit(stop = trail, limit = avg + 3 R);  rsi(high, 14) > 75 -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The target is fixed per trade: the fill price plus 3 x R of the signal bar, sent as a fraction of
      the fill (3 R / fill open). The stop is a ratchet re-computed every bar from the 10-bar low minus
      the ATR, which the house trail settings cannot express: not ported (mark trailing_stop_pending),
      so trades end at the target or the RSI close. Entries only from flat: a loop follows the target on
      the bar's high and the RSI close so the flat gate lines up (as 449508). The short side ("Short" /
      "Both") is a separate setting, not ported. The risk-based size is not ported. Long only. Stop
      module: portfolio_kwargs {} (driver D4). Stops on 2-hour bars: mark coarse_bar_stop. FREQ = "2h"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the R-multiple target as a fraction of the fill.
    2 generic: PASS, big-candle reversal pairs with an R target and an RSI exit; ratchet stop described (pending).
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: risk-based size stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_474670_parallel_candles_3r_target_rsi_exit_long_ratchet_pending"
FAMILY = "candle_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "lookback": [10, 20],
    "rr": [3.0, 2.0],
}
DEFAULT_PARAMS = {"lookback": 10, "rr": 3.0, "atr_len": 14, "atr_mult": 1.0, "rsi_up": 75}


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
    return 100 - 100 / (1 + up / dn)


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def _run(bars_df, p):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    rng = h - lo
    big = rng > rng.rolling(14).mean()
    bigred = ((o - c) / rng > 0.8) & big
    biggreen = ((c - o) / rng > 0.8) & big
    atr = _atr(bars_df, p["atr_len"])
    lc = (bigred.shift(1, fill_value=False) & biggreen & atr.notna()).to_numpy()
    r_sig = (c - (lo.rolling(int(p["lookback"])).min() - atr * float(p["atr_mult"]))).to_numpy(dtype=float)
    rx = (_rsi(h, 14) > float(p["rsi_up"])).to_numpy()
    ov, hv = o.to_numpy(dtype=float), h.to_numpy(dtype=float)
    rr = float(p["rr"])
    m = len(ov)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    r_sent = np.full(m, np.nan)
    pos, pend, tp, r_n = 0, 0, np.nan, np.nan
    for i in range(m):
        if pend == 1:
            pos, pend, tp = 1, 0, ov[i] + rr * r_n
        elif pend == 3:
            pos, pend, tp = 0, 0, np.nan
        if pos == 1 and hv[i] >= tp:
            pos, tp = 0, np.nan                  # the target fills inside this bar
        if pend != 0:
            continue
        if pos == 0 and lc[i]:
            r_n = r_sig[i]
            le[i], pend, r_sent[i] = True, 1, r_n
        elif pos == 1 and rx[i]:
            lx[i], pend = True, 3                # the RSI close: flat from the next open
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy(), pd.Series(r_sent, index=ix)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return tuple(_run(bars_df, p)[:4])


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    r_l = _run(bars_df, p)[4].shift(1)          # the signal bar's R, read at the fill
    tp_f = float(p["rr"]) * r_l / bars_df["open"]
    return {"tp_stop": tp_f.where(tp_f > 0)}


def portfolio_kwargs(**params):
    return {}
