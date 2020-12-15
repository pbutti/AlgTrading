
class Alg_EMAStrategy:

    # Trend Following – you essentially use the EMA to track the primary trend. If the stock does not close beyond the average – you stay in the trade.
    # Moving Average Crosses – by using two different exponential moving average crosses you can generate buy and/or sell signals. For example, you can have a fast average cross a slow average to trigger a trade signal.
    # Dynamic Support and Resistance – EMA periods like the 50 or 200 can act as support and resistance zones.

    # df holds the time serie of the security
    # fast is the fast EMA period
    # slow is the slow EMA period

    def __init__(self,df,fast=50,slow=200):
        self.data = df
        self.fast = fast
        self.slow = slow
