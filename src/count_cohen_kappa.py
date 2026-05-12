import numpy as np
from sklearn.metrics import cohen_kappa_score
from itertools import combinations


def pairwise_weighted_kappa(annotators, weights='quadratic'):
    """
    Calculate average pairwise weighted Cohen's Kappa for ordinal data (rankings)

    Args:
        annotators: list of lists, where each inner list is one annotator's rankings
                   e.g., [[1,2,3,1,2], [1,2,2,1,3], [1,3,3,1,2]] for 3 annotators
        weights: 'linear' or 'quadratic' (quadratic penalizes larger disagreements more)

    Returns:
        float: average of all pairwise weighted kappa scores
    """
    kappa_scores = []

    # Calculate weighted kappa for each pair of annotators
    for i, j in combinations(range(len(annotators)), 2):
        kappa = cohen_kappa_score(annotators[i], annotators[j], weights=weights)
        kappa_scores.append(kappa)
        print(f"Annotator {i + 1} vs Annotator {j + 1}: {kappa:.4f}")

    avg_kappa = np.mean(kappa_scores)
    return avg_kappa


# Example usage
if __name__ == "__main__":
    # 3 annotators ranking 9 items into groups 1-5
    # Some items can have the same rank (ties)
    annotator1 = [1, 4, 5, 5, 1, 4, 3, 3, 2, 2]
    annotator2 = [5, 5, 3, 3, 4, 4, 2, 1, 1, 2]
    annotator3 = [1, 2, 2, 3, 4, 5, 4, 3, 3, 3]

    annotators = [annotator1, annotator2, annotator3]

    print("QUADRATIC WEIGHTED KAPPA (recommended for rankings):")
    print("=" * 60)
    avg_kappa_quadratic = pairwise_weighted_kappa(annotators, weights='quadratic')
    print(f"\nAverage Pairwise Weighted Kappa (quadratic): {avg_kappa_quadratic:.4f}")

    print("\n" + "=" * 60)
    print("LINEAR WEIGHTED KAPPA:")
    print("=" * 60)
    avg_kappa_linear = pairwise_weighted_kappa(annotators, weights='linear')
    print(f"\nAverage Pairwise Weighted Kappa (linear): {avg_kappa_linear:.4f}")

    print("\n" + "=" * 60)
    print("UNWEIGHTED KAPPA (for comparison - not recommended for rankings):")
    print("=" * 60)
    avg_kappa_unweighted = pairwise_weighted_kappa(annotators, weights=None)
    print(f"\nAverage Pairwise Kappa (unweighted): {avg_kappa_unweighted:.4f}")