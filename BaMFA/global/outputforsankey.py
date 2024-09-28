import numpy as np
import pandas as pd

def output_for_sankey(output, availablechildflows, availablechildstocks,allflownumbersmatrix,countrylabel):
    """
    Function which creates a spreadsheet showing results of flows to use as a base for Sankey diagrams.
    """

    output_flownav = pd.DataFrame(columns=['flownumberfrom', 'flownumberto'])  # Define the columns explicitly
    for i in range(0, len(availablechildflows)):
        relevantrow = np.where(allflownumbersmatrix[:, 0] == str(availablechildflows[i]))
        relevantrow = relevantrow[0][0]
        flownumberfrom = allflownumbersmatrix[relevantrow, 1]
        flownumberto = allflownumbersmatrix[relevantrow, 2]

        # Add the values to the DataFrame
        output_flownav.loc[len(output_flownav)] = [flownumberfrom, flownumberto]

    # Create a DataFrame with two zero-filled columns
    output_stocknav = pd.DataFrame({'flownumberfrom': [0] * len(availablechildstocks),
                       'flownumberto': [0] * len(availablechildstocks)})

    # Create a DataFrame with two zero-filled columns
    output_parentnav = pd.DataFrame({'parentflownumberfrom': [0] * len(availablechildstocks+availablechildflows),
                       'parentflownumberto': [0] * len(availablechildstocks+availablechildflows)})

    output_fsnav = pd.concat([output_stocknav, output_flownav], ignore_index=True)
    output_nav = pd.concat([output_parentnav, output_fsnav], axis=1)
    output_nav['navigation'] = output_nav['flownumberfrom'].astype(str) + '-' + output_nav['flownumberto'].astype(str)+ '-' + output_nav['parentflownumberfrom'].astype(str) + '-' + output_nav['parentflownumberto'].astype(str)

    output['flownumberfrom'] = np.nan
    output['flownumberto'] = np.nan
    output['parentflownumberfrom'] = np.nan
    output['parentflownumberto'] = np.nan
    output['navigation'] = np.nan
    
    output['flownumberfrom'].iloc[:len(output_nav)] = output_nav['flownumberfrom'].astype(str).values
    output['flownumberto'].iloc[:len(output_nav)] = output_nav['flownumberto'].astype(str).values
    output['parentflownumberfrom'].iloc[:len(output_nav)] = output_nav['parentflownumberfrom'].astype(str).values
    output['parentflownumberto'].iloc[:len(output_nav)] = output_nav['parentflownumberto'].astype(str).values
    output['navigation'].iloc[:len(output_nav)] = output_nav['navigation'].astype(str).values

    original_columns = output.columns.tolist()
    columns_to_move = ['flownumberfrom', 'flownumberto', 'parentflownumberfrom', 'parentflownumberto', 'navigation']
    original_columns = [col for col in original_columns if col not in columns_to_move]
    # Define the new column order
    new_column_order = columns_to_move + original_columns
    # Reorder the columns in the DataFrame
    output = output[new_column_order]
    
    output.drop(output.index[:len(availablechildstocks)], inplace=True)
    output.drop(index=output.index[len(availablechildflows):], inplace=True)

    output.to_excel("results"+"/"+countrylabel+"/"+'outputforsankey-'+countrylabel+'.xlsx', sheet_name='output-'+countrylabel, index=True)