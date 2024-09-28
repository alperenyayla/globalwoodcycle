import numpy as np
from math import log10, floor

def round_to_poweroften(x):
    """
    Function which rounds a number to the nearest power of 10
    """

    if x == 0:
        ans = 0
    else:
        ans = np.sign(x) * 10 ** round(log10(abs(x)) - log10(5.5) + 0.5)
    return ans


def definepriors(datastockspriors, dataflowspriors, availabledatafull, m, N):

    """
    Function for defining vector of prior mean and covariance
    """
    
    datastockspriors=datastockspriors.loc[datastockspriors['ParentProcess'] == 0]
    
    dataflowspriors = dataflowspriors.loc[(dataflowspriors['ParentProcessFlowto'] == 0) & (dataflowspriors['ParentProcessFlowfrom'] == 0)]

    datastockspriors = datastockspriors[['Processnumber', 'quantity']]
    datastockspriors = datastockspriors.to_numpy()

    #dataflowspriors = dataflowspriors[['Flownumberfrom', 'Flownumberto', 'quantity']]
    dataflowspriors["Flownumber"] = m + (dataflowspriors["Flownumberfrom"]) * m + dataflowspriors["Flownumberto"]
    
    defaultval=dataflowspriors['quantity'].mean()
    
    dataflowspriors = dataflowspriors[['Flownumber', 'quantity']].to_numpy()
    
    priormean = np.array([defaultval] * N)
    covariancevec = 100.0 * (defaultval **2) * np.ones(N)

    truevalues = np.array([float('nan')] * N)

    covfactor = 42.0
    
    for row in availabledatafull:
        if row[0] < N:
            if np.isnan(row[1]) == False and row[1] != 0:
                 truevalues[int(row[0])] = row[1]

    for row in datastockspriors:
        priormean[int(row[0])] = row[1]
        covariancevec[int(row[0])] = max(covfactor * row[1] ** 2, 0.01)

        truevalues[int(row[0])] = row[1]

    for row in dataflowspriors:
        if row[1] == 0:  # priors can't be exactly 0 as that's on the boundary of the support, which causes pymc3 to fail
            priormean[int(row[0])] = row[1] + 0.001
            covariancevec[int(row[0])] = row[1] ** 2 + 0.001
        else:
            priormean[int(row[0])] = row[1]
            covariancevec[int(row[0])] = max(covfactor * row[1] ** 2, 0.01)

        truevalues[int(row[0])] = row[1]

    return priormean, covariancevec, truevalues