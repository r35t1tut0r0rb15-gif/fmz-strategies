"""Closes over a Keltner upper line (EMA 80 + 3 x EMA 80 of the true range) with the last two bars' volume over 1.5 times two bars before, hourly bars, long only: the entry price is the signal close plus 10 points; a close 6 % under it, a 10 % gain then a 10 % fall in 23 bars, or a close under the EMA 80 closes, except that a close under the EMA while more than 10 % up stops the bot for good (it keeps the long).
Port of FMZ strategy #313041 "Keltner通道突破止损加盈利10即长期持有策略-v23-dev-多周期" (Keltner通道突破止损加盈利10即长期持有策略-v23-dev-多周期).

FMZ source id: 313041

Source
    https://www.fmz.com/strategy/313041 (python, FMZ last modified 2021-09-02 12:04:56).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 27-146), EMA 80 Keltner x 3 of TRANGE; volume (v0 + v1) > 1.5 (v3 + v4); stop 6 %; last_price = close + 10; 600 USDT per buy
    flat and close > upper and (vol[0] + vol[1]) > 1.5 (vol[3] + vol[4]) -> Buy (600 USDT), last_price := close + 10
    held: close <= last x 0.94 -> sell;  elif close >= last x 1.1 and close <= close[23] x 0.9 -> sell;  elif close < ema80: close <= last -> sell; close > last x 1.1 -> return (main ends); last < close <= last x 1.1 -> sell

Interpretation choices (rules in SURVEY_README.md)
    * The bot polls the hourly records every 15 minutes, its last record being the forming bar; the port
      reads completed bars (SURVEY_README: bots polling the forming bar). The 10 added to the entry close
      is a price amount, read as a fraction of 42000 of the close (2.381e-04). The "return" leaves main()
      while the long is held, so the bot never trades again: the port keeps the long to the end of the
      data once that bar comes (a weird case, reported). The EMA 30 / SMA 30 and DI lines are computed but
      unused. The balance tests only mean "flat with cash". Long only. The 600 USDT buys are sizing.
      FREQ = "1h" from the source's records.

Admission criteria
    1 fits the interface: PASS, bar-close orders; close-based exits; a terminal halt kept as written.
    2 generic: PASS, Keltner breakouts with a volume surge filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 600 USDT per buy and balance tests stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the surge test (v0 + v1) > 1.5 (v3 + v4); exchange volume to be compared later (Austin, 2026-10-23).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_313041_keltner80_x3_break_volume_surge_pct_stops_halt_long"
FAMILY = "keltner_channel"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # the source's GetRecords(1 h)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "k": [3.0, 2.0],
    "vol_mult": [1.5, 2.0],
}
DEFAULT_PARAMS = {"k": 3.0, "vol_mult": 1.5, "ema_length": 80, "add_frac": 2.380952e-04}


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
    h, lo, c, v = bars_df["high"], bars_df["low"], bars_df["close"], bars_df["volume"]
    n = int(p["ema_length"])
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1).where(pc.notna())
    ma = c.ewm(span=n, adjust=False).mean()
    upper = ma + float(p["k"]) * tr.ewm(span=n, adjust=False).mean()
    surge = (v + v.shift(1)) > float(p["vol_mult"]) * (v.shift(3) + v.shift(4))
    go = ((c > upper) & surge).to_numpy()
    below = (c < ma).to_numpy()
    c23 = c.shift(23).to_numpy(dtype=float)
    cv = c.to_numpy(dtype=float)
    add = float(p["add_frac"])
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, last, halted = 0, np.nan, False
    for i in range(m):
        if halted:
            break                                  # main() returned: no more orders
        if pos == 0 and go[i]:
            le[i], pos, last = True, 1, cv[i] * (1 + add)
            continue
        if pos == 1:
            if cv[i] <= last * 0.94:
                lx[i], pos = True, 0
            elif cv[i] >= last * 1.1 and cv[i] <= c23[i] * 0.9:
                lx[i], pos = True, 0
            elif below[i]:
                if cv[i] <= last:
                    lx[i], pos = True, 0
                elif cv[i] > last * 1.1:
                    halted = True                  # "return": the long is kept for good
                elif cv[i] > last:
                    lx[i], pos = True, 0
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
