"""
File containing general methods for computing property statistics
"""
import numpy as np
from scipy import stats

from six import string_types


# TODO: some of this needs a bit more cleanup. The kernel methods (requiring two lists) should
# probably go in a different class. Some of the method signatures are consistent, others aren't.
# Just needs a 15 minute cleanup check. -computron

class PropertyStats(object):

    @staticmethod
    def calc_stat(data_lst, stat, weights=None):
        """
        Compute a property statistic

        Args:
            data_lst (list of floats): list of values
            stat (str) - Name of property to be compute. If there are arguments to the statistics function, these
             should be added after the name and separated by two underscores. For example, the 2nd Holder mean would
             be "holder_mean__2"
            weights (list of floats): (Optional) weights for each element in data_lst
        Return:
            float - Desired statistic
        """
        statistics = stat.split("__")
        return getattr(PropertyStats, statistics[0])(data_lst, weights, *statistics[1:])

    @staticmethod
    def minimum(data_lst, weights=None):
        """Minimum value in a list

        Args:
            data_lst (list of floats): List of values to be assessed
            weights (ignored)
        Returns: 
            minimum value
        """
        return min(data_lst) if float("nan") not in data_lst else float("nan")

    @staticmethod
    def maximum(data_lst, weights=None):
        """Maximum value in a list

        Args:
            data_lst (list of floats): List of values to be assessed
            weights (ignored)
        Returns: 
            maximum value
        """
        return max(data_lst) if float("nan") not in data_lst else float("nan")

    @staticmethod
    def range(data_lst, weights=None):
        """Range of a list

        Args:
            data_lst (list of floats): List of values to be assessed
            weights (ignored)
        Returns: 
            range
        """
        return (max(data_lst) - min(data_lst)) if float("nan") not in data_lst \
            else float("nan")

    @staticmethod
    def mean(data_lst, weights=None):
        """Arithmetic mean of list

        Args:
            data_lst (list of floats): List of values to be assessed
            weights (list of floats): Weights for each value
        Returns: 
            mean value
        """
        return np.average(data_lst, weights=weights)

    @staticmethod
    def inverse_mean(data_lst, weights=None):
        """Mean of the inverse of each entry

        Args:
            data_lst (list of floats): List of values to be assessed
            weights (list of floats): Weights for each value
        Returns:
            inverse mean
        """
        return PropertyStats.mean([1.0 / x for x in data_lst], weights=weights)

    @staticmethod
    def avg_dev(data_lst, weights=None):
        """Mean absolute deviation of list of element data.

        This is computed by first calculating the mean of the list, and then computing the average absolute difference
        between each value and the mean.

        Args:
            data_lst (list of floats): List of values to be assessed
            weights (list of floats): Weights for each value
        Returns: 
            mean absolute deviation
        """
        mean = PropertyStats.mean(data_lst, weights)
        return np.average(np.abs(np.subtract(data_lst, mean)), weights=weights)

    @staticmethod
    def std_dev(data_lst, weights=None):
        """Standard deviation of a list of element data

        Args:
            data_lst (list of floats): List of values to be assessed
            weights (list of floats): Weights for each value
        Returns:
            standard deviation
        """
        if weights is None:
            return np.std(data_lst)
        else:
            beta = np.sum(weights) / (np.sum(weights) ** 2 - np.sum(np.power(weights, 2)))
            dev = np.power(np.subtract(data_lst, PropertyStats.mean(data_lst, weights=weights)), 2)
            return np.sqrt(beta * np.dot(dev, weights))

    @staticmethod
    def geom_std_dev(data_lst, weights=None):
        """
        Geometric standard deviation

        Args:
            data_lst (list of floats): List of values to be assessed
            weights (list of floats): Weights for each value
        Returns:
            geometric standard deviation
        """

        # Make fake weights, if none are provided
        if weights is None:
            weights = np.ones_like(data_lst)

        # Compute the geometric std dev
        mean = PropertyStats.holder_mean(data_lst, weights, 0)
        beta = np.sum(weights) / (np.sum(weights) ** 2 - np.sum(np.power(weights, 2)))
        dev = np.log(np.divide(data_lst, mean))
        return np.sqrt(np.exp(beta * np.dot(weights, np.power(dev, 2))))

    @staticmethod
    def mode(data_lst, weights=None):
        """Mode of a list of data.

        If multiple elements occur equally-frequently (or same weight, if weights are provided), this function
        will return the average of those values.

        Args:
            data_lst (list of floats): List of values to be assessed
            weights (list of floats): Weights for each value
        Returns: 
            mode
        """
        if weights is None:
            return stats.mode(data_lst).mode[0]
        else:
            # Find the entry(s) with the largest weight
            data_lst = np.array(data_lst)
            weights = np.array(weights)
            most_freq = np.isclose(weights, weights.max())

            # Return the minimum of the most-frequent entries
            return data_lst[most_freq].min()

    @staticmethod
    def n_numerical_modes(data_lst, n, dl=0.1):
        """
        Returns the n first modes of a data set that are obtained with
            a finite bin size for the underlying frequency distribution.
        Args:
            data_lst ([float]): data values.
            n (integer): number of most frequent elements to be determined.
            dl (float): bin size of underlying (coarsened) distribution.
        Returns:
            ([float]): first n most frequent entries (or nan if not found).
        """
        if len(set(data_lst)) == 1:
            return [data_lst[0]] + [float('NaN') for _ in range(n-1)]
        hist, bins = np.histogram(data_lst, bins=np.arange(
                min(data_lst), max(data_lst), dl), density=False)
        modes = list(bins[np.argsort(hist)[-n:]][::-1])
        return modes + [float('NaN') for _ in range(n-len(modes))]

    @staticmethod
    def holder_mean(data_lst, weights=None, power=1):
        """
        Get Holder mean
        Args:
            data_lst: (list/array) of values
            weights: (list/array) of weights
            power: (int/float/str) which holder mean to compute
        Returns: Holder mean
        """

        if isinstance(power, string_types):
            power = float(power)

        if weights is None:
            if power == 0:
                return stats.mstats.gmean(data_lst)
            else:
                return np.power(np.mean(np.power(data_lst, power)), 1.0 / power)
        else:
            # Compute the normalization factor
            alpha = sum(weights)

            # If power=0, return geometric mean
            if power == 0:
                return np.product(np.power(data_lst, np.divide(weights, np.sum(weights))))
            else:
                return np.power(np.sum(np.multiply(weights, np.power(data_lst, power))) / alpha, 1.0/power)

    @staticmethod
    def sorted(data_lst):
        """
        Returns the sorted data_lst
        """
        return np.sort(data_lst)

    @staticmethod
    def eigenvalues(data_lst, symm = False, sort = False):
        """
        Return the eigenvalues of a matrix as a numpy array
        Args:
            data_lst: (matrix-like) of values
            symm: whether to assume the matrix is symmetric
            sort: wheter to sort the eigenvalues
        Returns: eigenvalues
        """
        eigs = np.linalg.eigvalsh(data_lst) if symm else np.linalg.eigvals(data_lst)
        if sort:
            eigs.sort()
        return eigs

    @staticmethod
    def flatten(data_lst):
        """Returns a flattened copy of data_lst-as a numpy array
        """
        return np.array(data_lst).flatten()

    @staticmethod
    def laplacian_kernel(arr0, arr1, SIGMA):
        """
        Returns a Laplacian kernel of the two arrays
        for use in KRR or other regressions using the
        kernel trick.
        """
        diff = arr0 - arr1
        return np.exp(-np.linalg.norm(diff.A1, ord=1) / SIGMA)

    @staticmethod
    def gaussian_kernel(arr0, arr1, SIGMA):
        """
        Returns a Gaussian kernel of the two arrays
        for use in KRR or other regressions using the
        kernel trick.
        """
        diff = arr0 - arr1
        return np.exp(-np.linalg.norm(diff.A1, ord=2)**2 / 2 / SIGMA**2)
