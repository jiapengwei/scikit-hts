import numpy

from _t import MethodsT
from hts import InvalidArgumentException
from hts.functions import y_hat_matrix, optimal_combination, proportions, forecast_proportions


class RevisionMethod(object):

    def __init__(self,
                 name: str,
                 sum_mat,
                 transformer,
                 ):
        self.name = name
        self.transformer = transformer
        self.sum_mat = sum_mat

    def _new_mat(self, y_hat_mat):
        new_mat = numpy.empty([y_hat_mat.shape[0], self.sum_mat.shape[0]])
        for i in range(y_hat_mat.shape[0]):
            new_mat[i, :] = numpy.dot(self.sum_mat, numpy.transpose(y_hat_mat[i, :]))
        return new_mat

    def _y_hat_matrix(self, forecasts):
        n_cols = len(list(forecasts.keys())) + 1
        keys = range(n_cols - self.sum_mat.shape[1] - 1, n_cols - 1)
        return y_hat_matrix(forecasts, keys=keys)

    def predict(self, forecasts=None, mse=None, df=None, nodes=None):
        if self.name in [MethodsT.OLS.name, MethodsT.WLSS.name, MethodsT.WLSV.name]:
            return optimal_combination(forecasts=forecasts,
                                       sum_mat=self.sum_mat,
                                       method=MethodsT.OLS.name,
                                       mse=mse)

        elif self.name == MethodsT.BU.name:
            y_hat = self._y_hat_matrix(forecasts)
            return self._new_mat(y_hat)

        elif self.name in [MethodsT.AHP.name, MethodsT.PHA.name]:
            if self.transformer:
                for column in range(len(df.columns.tolist()) - 1):
                    df.iloc[:, column + 1] = self.transformer.inverse_transform(df.iloc[:, column + 1])
            y_hat = proportions(df, forecasts, self.sum_mat, method=self.name)
            return self._new_mat(y_hat)

        elif self.name == MethodsT.FP.name:
            return forecast_proportions(forecasts, nodes)

        else:
            raise InvalidArgumentException('Revision model name is invalid')

