import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import random

def preprocessing(datastocks, dataflows):

    """
    Function for preprocessing stock and flow dataset
    """

    datachildstocks = datastocks.loc[datastocks['ParentProcess'] == 0]

    dataparentstocks = datastocks.loc[datastocks['ParentProcess'] == 1]

    childstocks = datachildstocks.Process.unique()

    m = len(childstocks)

    N = m + m * m

    Flownumberfromvector = list(range(0, m))

    for i in range(0, m):
        Flownumberfromvector = Flownumberfromvector + [i] * m

    Flownumbertovector = ['nan'] * m
    for i in range(0, m):
        Flownumbertovector = Flownumbertovector + list(range(0, m))

    Flownumberfromvector = np.reshape(Flownumberfromvector, (len(Flownumberfromvector), 1))

    Flownumbertovector = np.reshape(Flownumbertovector, (len(Flownumbertovector), 1))


    allflownumbersmatrix = np.hstack(((np.reshape(list(range(0, N)), (N, 1)), Flownumberfromvector, Flownumbertovector)))

    processnamesdict = pd.Series(datachildstocks.Process.values,index=datachildstocks.Processnumber.astype(str)).to_dict()

    processnamesdict['nan'] = 'Stock'

    parentstocks = dataparentstocks.Process.unique()

    M = len(parentstocks)

    largenumber = 1
    while largenumber < 2 * max(N, M + M * M):
        largenumber = largenumber * 10

    dataflows["Flownumber"] = np.where(dataflows['ParentProcessFlowto'] + dataflows['ParentProcessFlowfrom'] >= 1,
                                       max(m, M) + (dataflows["Flownumberfrom"]) * max(m, M) + dataflows["Flownumberto"],
                                       m + (dataflows["Flownumberfrom"]) * m + dataflows["Flownumberto"])


    datastocks.loc[datastocks['ParentProcess'] == 1, ['Processnumber']] += largenumber

    dataparentstocks = datastocks.loc[datastocks['ParentProcess'] == 1]

    dataparentstockneededcols = dataparentstocks[['Processnumber', 'quantity', 'Subprocessnumbers', 'Process']]
    dataparentstockneededcols = dataparentstockneededcols.to_numpy()

    dataflows.loc[dataflows['ParentProcessFlowfrom'] == 1, ['Flownumberfrom']] += largenumber
    dataflows.loc[dataflows['ParentProcessFlowto'] == 1, ['Flownumberto']] += largenumber
    dataflows.loc[dataflows['ParentProcessFlowfrom'] == 1, ['Flownumber']] += largenumber
    dataflows.loc[dataflows['ParentProcessFlowto'] == 1, ['Flownumber']] += largenumber

    dataparentinflows = dataflows.loc[(dataflows['ParentProcessFlowto'] == 1) & (dataflows['ParentProcessFlowfrom'] == 0)]
    dataparentoutflows = dataflows.loc[(dataflows['ParentProcessFlowfrom'] == 1) & (dataflows['ParentProcessFlowto'] == 0)]
    dataparentbothflows = dataflows.loc[(dataflows['ParentProcessFlowto'] == 1) & (dataflows['ParentProcessFlowfrom'] == 1)]

    dataparentinflowneededcols = dataparentinflows[['Flownumber', 'quantity', 'Flownumberfrom', 'Subprocessnumbersto', 'From', 'to']]
    dataparentoutflowneededcols = dataparentoutflows[['Flownumber', 'quantity', 'Subprocessnumbersfrom', 'Flownumberto', 'From', 'to']]
    dataparentbothflowsneededcols = dataparentbothflows[['Flownumber', 'quantity', 'Subprocessnumbersfrom', 'Subprocessnumbersto', 'From', 'to']]

    dataparentinflowneededcols = dataparentinflowneededcols.to_numpy()
    dataparentoutflowneededcols = dataparentoutflowneededcols.to_numpy()
    dataparentbothflowsneededcols = dataparentbothflowsneededcols.to_numpy()
    dataparentflowsneededcols = np.concatenate((dataparentinflowneededcols, dataparentoutflowneededcols, dataparentbothflowsneededcols))


    availablestocksfull = np.copy(datastocks.Processnumber.unique())
    availableflowsfull = np.copy(dataflows.Flownumber.unique())
    availablestockdatafull = datastocks.quantity.to_numpy()
    availableflowdatafull = dataflows.quantity.to_numpy()
    availablestocksandflowsfull = np.concatenate((availablestocksfull, availableflowsfull))
    availablestockandflowdatafull = np.concatenate((availablestockdatafull, availableflowdatafull))


    availabledatafull = np.column_stack((availablestocksandflowsfull, availablestockandflowdatafull))

    availabledatafulldataframe = pd.DataFrame({'Flownumber': availablestocksandflowsfull.astype(int), 'quantity': availablestockandflowdatafull})

    availabledatafulldict = pd.Series(availabledatafulldataframe.quantity.values,index=availabledatafulldataframe.Flownumber.astype(str)).to_dict()


    outputdatachildprocess = pd.DataFrame({'Flownumber': allflownumbersmatrix[:, 0], 'Flownumberfrom': allflownumbersmatrix[:, 1],'Flownumberto': allflownumbersmatrix[:, 2]})
    outputdatachildprocess['From'] = outputdatachildprocess['Flownumberfrom'].astype(str).map(processnamesdict)
    outputdatachildprocess['To'] = outputdatachildprocess['Flownumberto'].astype(str).map(processnamesdict,na_action='ignore')
    outputdatachildprocess['quantity'] = outputdatachildprocess['Flownumber'].map(availabledatafulldict)

    return availabledatafull, dataparentstockneededcols, dataparentflowsneededcols, processnamesdict, allflownumbersmatrix, m, N




def createdesignmatrix(availabledatafull, dataparentstockneededcols, dataparentflowsneededcols, m, N):

    """
    Create design matrix for linear data based on preprocessed data
    """

    designmatrix = np.empty((1, N))
    datavector = []
    availablechildstocksandflows = []

    zerostocksandflows = []

    dataflownumber = []
    stockflownumber = []
    flowflownumber = []
    CoMflownumber = []

    stockindex = []
    flowindex = []
    CoMindex = []

    for row in availabledatafull:
        if row[0] < N:
            availablechildstocksandflows.append(int(row[0]))
            if np.isnan(row[1]) == False and row[1] != 0:  # note this includes the nan stocks
                newrow = np.zeros((1, N))
                newrow[:, int(row[0])] = 1
                datavector.append(row[1])
                designmatrix = np.vstack([designmatrix, newrow])

                dataflownumber.append(row[0])
                if row[0] < m:
                    stockflownumber.append(row[0])
                    stockindex.append(len(datavector) - 1)
                else:
                    flowflownumber.append(row[0])
                    flowindex.append(len(datavector) - 1)
            if row[1] == 0:
                zerostocksandflows.append(int(row[0]))


    for row in dataparentstockneededcols:
        subprocesses = row[2].split("-")
        subprocesses = list(map(int, subprocesses))
        subprocesses.sort()
        newrow = np.zeros((1, N))
        for i in subprocesses:
            availablechildstocksandflows.append(int(i))
        if np.isnan(row[1]) == False and row[1] != 0:
            for i in subprocesses:
                newrow[:, int(i)] = 1
            datavector.append(row[1])
            designmatrix = np.vstack([designmatrix, newrow])

            dataflownumber.append(row[0])
            stockflownumber.append(row[0])
            stockindex.append(len(datavector) - 1)

        if row[1] == 0:
            for i in subprocesses:
                zerostocksandflows.append(int(i))

    for row in dataparentflowsneededcols:
        subprocessesfrom = str(row[2]).split("-")
        subprocessesfrom = list(map(int, subprocessesfrom))
        subprocessesfrom.sort()
        subprocessesto = str(row[3]).split("-")
        subprocessesto = list(map(int, subprocessesto))
        subprocessesto.sort()
        newrow = np.zeros((1, N))

        for processfrom in subprocessesfrom:
            for processto in subprocessesto:
                availablechildstocksandflows.append(int((processfrom + 1) * m + processto))

        if np.isnan(row[1]) == False and row[1] != 0:
            for processfrom in subprocessesfrom:
                for processto in subprocessesto:
                    newrow[:, int((processfrom + 1) * m + processto)] = 1
            datavector.append(row[1])
            designmatrix = np.vstack([designmatrix, newrow])

            dataflownumber.append(row[0])
            flowflownumber.append(row[0])
            flowindex.append(len(datavector) - 1)
        if row[1] == 0:
            for processfrom in subprocessesfrom:
                for processto in subprocessesto:
                    zerostocksandflows.append(int((processfrom + 1) * m + processto))

    # add conservation of mass to design matrix
    for i in range(0, m):
        newrow = np.zeros((1, N))
        # set stock to 1
        newrow[:, int(i)] = 1

        for j in range(0, m):
            # set the inflows to -1
            newrow[:, int(i + (j + 1) * m)] = -1
            # set the outflows to 1
            newrow[:, int((i + 1) * m + j)] = 1

        datavector.append(0)
        designmatrix = np.vstack([designmatrix, newrow])

        dataflownumber.append(-2)
        CoMflownumber.append(-2)
        CoMindex.append(len(datavector) - 1)


    designmatrix = np.delete(designmatrix, (0), axis=0)
    datavector = np.array(datavector)

    return designmatrix, datavector, availablechildstocksandflows, zerostocksandflows, stockindex, flowindex, CoMindex


def createratiomatrix(dataratios, m, N, availablechildstocksandflows):

    """
    Create matrices for ratio data
    """

    dataratios = dataratios.to_numpy()

    ratiomatrixtop = np.empty((1, N))
    ratiomatrixbottom = np.empty((1, N))
    sigmaratiovector = []
    ratiovector = []

    for row in dataratios:

        subprocessesfromtop = str(row[2]).split("-")
        subprocessesfromtop = list(map(int, subprocessesfromtop))

        subprocessestotop = str(row[3]).split("-")
        subprocessestotop = list(map(int, subprocessestotop))

        subprocessesfrombottom = str(row[6]).split("-")
        subprocessesfrombottom = list(map(int, subprocessesfrombottom))

        subprocessestobottom = str(row[7]).split("-")
        subprocessestobottom = list(map(int, subprocessestobottom))

        ratio = row[8]

        sigmaratiocurrent = 0
        newrowtop = np.zeros((1, N))
        newrowbottom = np.zeros((1, N))
        for processfrom in subprocessesfromtop:
            for processto in subprocessestotop:
                newrowtop[:, int((processfrom + 1) * m + processto)] = 1

                availablechildstocksandflows.append(int((processfrom + 1) * m + processto))

        for processfrom in subprocessesfrombottom:
            for processto in subprocessestobottom:
                newrowbottom[:, int((processfrom + 1) * m + processto)] = 1

                sigmaratiocurrent = (0.1 * ratio)

                availablechildstocksandflows.append(int((processfrom + 1) * m + processto))

        ratiomatrixtop = np.vstack([ratiomatrixtop, newrowtop])
        ratiomatrixbottom = np.vstack([ratiomatrixbottom, newrowbottom])
        sigmaratiovector.append(sigmaratiocurrent)
        ratiovector.append(ratio)

    ratiovector = np.array(ratiovector)
    ratiomatrixtop = np.delete(ratiomatrixtop, (0), axis=0)
    ratiomatrixbottom = np.delete(ratiomatrixbottom, (0), axis=0)

    return ratiovector, ratiomatrixtop, ratiomatrixbottom, availablechildstocksandflows

def createcompactmatrix(designmatrix,availablechildstocksandflows,m):

    """
    Create smaller matrix for the design matrix after removing stock and flow variables that don't exist in the system
    """

    availablechildstocks = [i for i in availablechildstocksandflows if i < m]
    availablechildflows = [i for i in availablechildstocksandflows if i >= m]

    designmatrixcompact = designmatrix[:, availablechildstocksandflows]
    designmatrixstockscompact = designmatrix[:, availablechildstocks]
    designmatrixflowscompact = designmatrix[:, availablechildflows]

    return designmatrixcompact,designmatrixstockscompact,designmatrixflowscompact

def createcompactratiomatrix(ratiomatrixtop,ratiomatrixbottom,availablechildstocksandflows,m):

    """
    Create smaller matrices for the ratio data after removing stock and flow variables that don't exist in the system
    """

    availablechildstocks = [i for i in availablechildstocksandflows if i < m]
    availablechildflows = [i for i in availablechildstocksandflows if i >= m]

    ratiomatrixtopstockscompact = ratiomatrixtop[:, availablechildstocks]
    ratiomatrixtopflowscompact = ratiomatrixtop[:, availablechildflows]

    ratiomatrixbottomstockscompact = ratiomatrixbottom[:, availablechildstocks]
    ratiomatrixbottomflowscompact = ratiomatrixbottom[:, availablechildflows]

    return ratiomatrixtopstockscompact,ratiomatrixtopflowscompact,ratiomatrixbottomstockscompact,ratiomatrixbottomflowscompact