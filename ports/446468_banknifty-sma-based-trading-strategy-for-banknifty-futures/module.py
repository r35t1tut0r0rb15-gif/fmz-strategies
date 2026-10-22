"""SMA 200 rejections, 5-minute bars, from flat: after a bar that straddled the SMA, a bar whose body is wholly above it goes long and wholly below goes short; a close back across the SMA, a 20-point loss or
a 150-point gain from the fill, or the 15:00 UTC hour closes.
Port of FMZ strategy #446468 "基于均线的BankNifty期货交易策略-SMA-based-Trading-Strategy-for-BankNifty-Futures" (Strategy BankNifty SMA).

FMZ source id: 446468

Source
    https://www.fmz.com/strategy/446468 (PineScript v5, FMZ last modified 2024-03-28 18:15:32).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 92-158), chart time frame 5 (MA source), SMA 200; stop-loss candle time frame 1; buffer 0; alert precision 0; target 150, stop 20 points; qty 15; margins 100 / 100
    touch = high[1] > sma[1] and low[1] < sma[1];  touch and min(open, close) > sma and flat -> entry buy (15);  touch and max(open, close) < sma and flat -> entry sell (15)
    longexit = slClose < sma or slClose < entry - 20 or slClose > entry + 150 or hour == 15 -> close buy;  shortexit mirrored -> close sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The source has no backtest header; its "chart time frame" input is 5 minutes, which the port
      takes as the bar size (FREQ = "5min"). The 5-minute request is then the chart's own close and
      the 1-minute request returns the last minute inside each bar, the bar's close. Criterion 2: the
      points are fractions of the fill price, 0.000476 (20) and 0.00357 (150), against BTC near 42000;
      they are bar-close tests filled at the next open. hour(time) is read on the bar's UTC open time
      (the exchange time zone, as #435514), so every bar of the 15:00 UTC hour closes a position; the
      Asia/Kolkata h / m values are never used. BankNifty is in the title only; the rules are generic.
      Entries only from flat, so positions never reverse. The qty 15 is sizing.

Admission criteria
    1 fits the interface: PASS, bar-close orders; exits are close tests against the fill.
    2 generic: PASS, SMA rejections with SMA, point and clock exits.
    3 crypto-exchange-only: no (BankNifty in the title only; no exchange header; the point values read as fractions of the price).
    4 signals only: the qty 15 and the margins stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: the 15:00 UTC hour closes positions (exchange time zone, no DST).
Opposite entries cannot occur (entries only from flat).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_446468_sma200_body_rejection_point_exits_5m"
FAMILY = "ma_pullback"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "5min"  # the source's chart time frame input (no backtest header)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [200, 100],
    "target_frac": [0.00357, 0.01],
}
DEFAULT_PARAMS = {"length": 200, "target_frac": 0.00357, "stop_frac": 0.000476, "exit_hour": 15}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    sma = c.rolling(int(p["length"])).mean()
    touch = (h.shift(1) > sma.shift(1)) & (lo.shift(1) < sma.shift(1))
    up = (touch & (np.minimum(o, c) > sma)).to_numpy()
    dn = (touch & (np.maximum(o, c) < sma)).to_numpy()
    clk = np.asarray(bars_df.index.hour == int(p["exit_hour"]))
    ov, cv, sv = o.to_numpy(dtype=float), c.to_numpy(dtype=float), sma.to_numpy()
    sf, tf = float(p["stop_frac"]), float(p["target_frac"])
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, fp = 0, np.nan
    with np.errstate(invalid="ignore"):
        for i in range(m):
            if pos == 0:
                if up[i]:
                    le[i], pos = True, 1
                elif dn[i]:
                    se[i], pos = True, -1
                if pos != 0:
                    fp = ov[i + 1] if i + 1 < m else np.nan   # the fill: the next bar's open
                continue
            if pos == 1 and (cv[i] < sv[i] or cv[i] < fp * (1 - sf) or cv[i] > fp * (1 + tf) or clk[i]):
                lx[i], pos = True, 0
            elif pos == -1 and (cv[i] > sv[i] or cv[i] > fp * (1 + sf) or cv[i] < fp * (1 - tf) or clk[i]):
                sx[i], pos = True, 0
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
