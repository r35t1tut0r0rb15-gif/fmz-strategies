"""Breakouts of a strong previous candle confirmed by two 15-minute MACD histograms, 1-hour bars: when the previous bar's body is 1.5 times its wicks, a close two or three bars back beyond that bar's high (low) goes long (short) if both 15-minute MACD histograms are positive and rising (negative and falling); reversing.
Port of FMZ strategy #472938 "双重MACD价格行为突破追踪策略-Dual-MACD-Price-Action-Breakout-Trailing-Strategy" (Price Action + Double MACD Strategy with ATR Trailing).

FMZ source id: 472938

Source
    https://www.fmz.com/strategy/472938 (PineScript v5, FMZ last modified 2024-11-25 11:15:50).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 103-205), MACD 34 / 144 / 9 and 100 / 200 / 50 colours on request.security("15"); strong candle = body > 1.5 x wicks; closes from request.security("5"); ATR 14 x 1 stop, x 1.5 ratcheting target
    new 15-minute period (every 1-hour bar) -> reset flags; strong previous candle -> level high[1] / low[1]
    for i = 1 to 3: close5[i] > level high and not traded -> (MACD up colours) entry Long, break;  close5[i] < level low -> (MACD down colours) entry Short, break
    traded and long -> exit(stop, limit = max(target, close + 1.5 atr));  traded and short -> mirrored;  flat -> reset

Interpretation choices (Pine rules in SURVEY_README.md)
    * On a 1-hour chart time("15") changes on every bar, so the flags reset on every bar. The "5" request
      is read as the chart bar's last 5-minute bar (#436765): its close is the 1-hour close, so
      close5[i] are the closes 1 to 3 bars back (close[1] can never exceed high[1]). The MACD colours
      are computed on 15-minute bars from the minutes and read on the chart bar's last 15-minute bar
      (#436765). Because the flags reset at the start of every bar, the exit is only sent on a bar that
      also enters while already holding; it is not ported (as #437800, mark trailing_stop_pending), and
      positions end at the opposite entry. REVERSAL INTENDED. No sizing code. FREQ = "1h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; 15-minute values from completed 15-minute bars.
    2 generic: PASS, strong-candle breakouts with double-MACD confirmation; armed exits described (pending).
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_472938_strong_candle_breakout_double_macd_15m_colours_reversal"
FAMILY = "macd_momentum"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "strong_k": [1.5, 1.0],
}
DEFAULT_PARAMS = {"strong_k": 1.5}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _colours(c, f, s, g):
    macd = c.ewm(span=f, adjust=False).mean() - c.ewm(span=s, adjust=False).mean()
    hist = macd - macd.ewm(span=g, adjust=False).mean()
    rising = hist.shift(1) < hist
    up = (hist >= 0) & rising                    # #26A69A
    dn = (hist < 0) & ~rising & hist.notna()     # #FF5252
    return up, dn


def precompute(raw_1m_df, symbol_key, **params):
    bars = _resample(raw_1m_df, FREQ)
    raw = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    c15 = raw["close"].resample("15min", label="left", closed="left").last().dropna()
    u1, d1 = _colours(c15, 34, 144, 9)
    u2, d2 = _colours(c15, 100, 200, 50)
    end15 = c15.index.to_numpy().astype("datetime64[ns]") + np.timedelta64(15, "m")
    end60 = bars.index.to_numpy().astype("datetime64[ns]") + np.timedelta64(60, "m")
    k = np.searchsorted(end15, end60, side="right") - 1          # last 15-minute bar completed by the close
    ok = k >= 0
    kk = np.clip(k, 0, None)
    bars["macd_up"] = np.where(ok, (u1 & u2).to_numpy()[kk], False)
    bars["macd_dn"] = np.where(ok, (d1 & d2).to_numpy()[kk], False)
    return bars


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    body = (c - o).abs()
    strong = (body > ((h - lo) - body) * float(p["strong_k"])).shift(1, fill_value=False).to_numpy()
    lvl_h, lvl_l = h.shift(1).to_numpy(), lo.shift(1).to_numpy()
    cv = c.to_numpy(dtype=float)
    up = bars_df["macd_up"].to_numpy(dtype=bool)
    dn = bars_df["macd_dn"].to_numpy(dtype=bool)
    m = len(cv)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    for t in range(m):
        if not strong[t]:
            continue
        for i in (1, 2, 3):
            if t - i < 0:
                break
            if cv[t - i] > lvl_h[t]:
                le[t] = bool(up[t])
                break
            if cv[t - i] < lvl_l[t]:
                se[t] = bool(dn[t])
                break
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
