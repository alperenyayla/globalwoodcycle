import numpy as np
import pymc3 as pm
import arviz as az

from pymc3 import TruncatedNormal, Normal, MvNormal, HalfCauchy, InverseGamma, Model, glm, \
    plot_posterior_predictive_glm, sample, Lognormal

from preprocessingagg import createcompactmatrix,createcompactratiomatrix

sigmastd=0.5

def mfamodel(priormean, covariancevec, designmatrix,ratiomatrixtop, \
                   ratiomatrixbottom, datavector, ratiovector, availablechildstocksandflows, m, \
                   stockindex, flowindex, CoMindex,useratiodata,sigmadeterministic=0):
    """
    Function for Bayesian model

    Arguments:
        priormean: prior mean of flow and change in stock variables
        covariancevec: diagonal of prior covariance matrix
        designmatrix: matrix for linear data
        ratiomatrixtop, ratiomatrixbottom: matrix for ratio data
        datavector: vector of data values for flow and change in stock values, as well as 0 for each conservation of mass conditions
        ratiovector: vector of ratio data values
        availablechildstocksandflows: list of indices to denote flow and change in stock variables that are non zero in the system
        m: number of processes in the system
        stockindex,flowindex,CoMindex: indices of datavector that splits it into stock data, flow data and conservation of mass conditions respectively
        userratiodata: whether to use ratio data, to split scenario A and B
        sigmadeterminstic: whether to elicit prior on the data noise variable
    """
    availablechildstocks = [i for i in availablechildstocksandflows if i < m]
    availablechildflows = [i for i in availablechildstocksandflows if i >= m]

    designmatrixcompact,designmatrixstockscompact,designmatrixflowscompact=createcompactmatrix(designmatrix, availablechildstocksandflows, m)
    ratiomatrixtopstockscompact,ratiomatrixtopflowscompact,ratiomatrixbottomstockscompact,ratiomatrixbottomflowscompact=createcompactratiomatrix(ratiomatrixtop, ratiomatrixbottom, availablechildstocksandflows, m)

    with Model() as model:

        if sigmadeterministic == 0:

            sigmastocks = InverseGamma("sigmastocks", alpha=4.0,
                                       beta=3.0 * np.maximum(np.abs(datavector[stockindex]) / 10, 0.1),
                                       shape=datavector[stockindex].shape[0])

            sigmaflows = InverseGamma("sigmaflows", alpha=4.0,
                                      beta=3.0 * np.maximum(np.abs(datavector[flowindex]) / 10, 0.1),
                                      shape=datavector[flowindex].shape[0])
            if useratiodata == 1:
                sigmaratio = InverseGamma("sigmaratio", alpha=4.0, beta=3.0 * np.maximum(0.1 * ratiovector, 0.01),
                                          shape=ratiovector.shape[0])
        else:
            sigmastocks = np.maximum(np.abs(datavector[stockindex]) / 10, 0.1)
            sigmaflows = np.maximum(np.abs(datavector[flowindex]) / 10, 0.1)
            if useratiodata == 1:
                sigmaratio = np.maximum(0.1 * ratiovector, 0.01)

        betastocks = pm.Normal('stocks', mu=priormean[availablechildstocks],
                               sigma=np.sqrt(covariancevec[availablechildstocks]),
                               shape=priormean[availablechildstocks].shape[0])

        betaflows = pm.TruncatedNormal('flows', mu=priormean[availablechildflows],
                                       sigma=np.sqrt(covariancevec[availablechildflows]), lower=0,
                                       shape=priormean[availablechildflows].shape[0])

        betadata = pm.Deterministic('datavars', var=pm.math.dot(designmatrixstockscompact, betastocks) + pm.math.dot(
            designmatrixflowscompact, betaflows))

        # Define likelihood
        likelihoodstocks = pm.Normal("stockdata", mu=pm.math.dot(designmatrixstockscompact[stockindex, :], betastocks)
                                                     + pm.math.dot(designmatrixflowscompact[stockindex, :], betaflows)
                                     ,sigma=sigmastocks,observed=datavector[stockindex])  # np.abs(datavector[stockindex])/10

        likelihoodflows = pm.TruncatedNormal("flowdata",
                                             mu=pm.math.dot(designmatrixstockscompact[flowindex, :], betastocks)
                                                + pm.math.dot(designmatrixflowscompact[flowindex, :], betaflows)
                                             ,sigma=sigmaflows, lower=0.0, observed=datavector[flowindex])  # np.abs(datavector[flowindex])/10

        if useratiodata == 1:
            likelihoodratio = pm.Normal("ratiodata", mu=(pm.math.dot(ratiomatrixtopstockscompact, betastocks)
                                                         + pm.math.dot(ratiomatrixtopflowscompact, betaflows)) / (pm.math.dot(ratiomatrixbottomstockscompact,betastocks)
                                                                    + pm.math.dot(ratiomatrixbottomflowscompact,betaflows))
                                        ,sigma=sigmaratio,observed=ratiovector)  # sigma=np.maximum(sigmavector[ratioindex],0.1)

        likelihoodmassconserve = pm.Normal("CoM", mu=pm.math.dot(designmatrixstockscompact[CoMindex, :], betastocks)
                                                     + pm.math.dot(designmatrixflowscompact[CoMindex, :], betaflows)
                                           ,sigma=sigmastd,observed=datavector[CoMindex])  # sigmastd+np.abs(datavector[CoMindex])/10

        # likelihood = pm.Normal("y", mu=pm.math.dot(designmatrixstockscompact, betastocks) + pm.math.dot(designmatrixflowscompact, betaflows), sigma=sigmastd, observed=datavector)

        trace = sample(10000, return_inferencedata=True, chains=2, init='jitter+adapt_diag', tune=2000,
                       target_accept=0.95, random_seed=123456)

    return trace, model
