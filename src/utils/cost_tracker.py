class CostTracker:
    """Simple cost tracking for API usage"""
    
    # Claude Sonnet 4 pricing (as of Dec 2024)
    INPUT_COST_PER_1M = 3.00   # $3 per 1M input tokens
    OUTPUT_COST_PER_1M = 15.00  # $15 per 1M output tokens
    
    def __init__(self):
        self.total_input_tokens = 0
        self.total_output_tokens = 0
    
    def add_usage(self, input_tokens: int, output_tokens: int):
        """Track token usage"""
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
    
    def get_estimated_cost(self) -> float:
        """Calculate estimated cost in USD"""
        input_cost = (self.total_input_tokens / 1_000_000) * self.INPUT_COST_PER_1M
        output_cost = (self.total_output_tokens / 1_000_000) * self.OUTPUT_COST_PER_1M
        return input_cost + output_cost
    
    def get_summary(self) -> dict:
        """Get usage summary"""
        return {
            "input_tokens": self.total_input_tokens,
            "output_tokens": self.total_output_tokens,
            "estimated_cost_usd": round(self.get_estimated_cost(), 4),
            "trips_remaining_in_20_budget": int(20 / self.get_estimated_cost()) if self.get_estimated_cost() > 0 else 0
        }