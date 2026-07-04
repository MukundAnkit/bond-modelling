class BinomialTree:
    def __init__(self, r0, volatility, time_step, periods):
        self.r0 = r0
        self.volatility = volatility
        self.time_step = time_step
        self.periods = periods

    def build_tree(self):
        # TODO: Implement tree building
        return [[0.0]]
        
    def get_probabilities(self):
        # TODO: Implement probabilities
        return {'p_up': 0.0, 'p_down': 0.0}
        
    def price_zero_coupon_bond(self, face_value):
        # TODO: Implement bond pricing
        return 0.0
