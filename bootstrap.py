import numpy as np

def bootstrap(count, total, depth=1000, smoothing=1, seed=42):
    if seed is not None:
        np.random.seed(seed)  # Set random seed to ensure consistent error margins
    if total != 1: # Not a decimal
        # Laplace smoothing-- Note: Removed
        smoothed_count = count # + smoothing
        smoothed_total = total # + 2 * smoothing
        # Simulate the binomial distribution
        bootstraped_counts = np.random.binomial(smoothed_total, smoothed_count / smoothed_total, size=depth)
    else:
        bootstraped_counts = np.random.binomial(total * 10000, count / total, size=depth)
    # Calculate the 95% confidence interval
    bootstraped_lower = np.percentile(bootstraped_counts, 2.5)
    bootstraped_upper = np.percentile(bootstraped_counts, 97.5)
    bootstraped_std = (bootstraped_upper - bootstraped_lower) / 2

    return [count, bootstraped_std / 10000 if total == 1 else round(bootstraped_std)] # List of sampled count and the margin of error up or down
