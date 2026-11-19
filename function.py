import numpy as np
import pandas as pd
from scipy import stats
from pathlib import Path


def statistical_test(file_name: str ) -> dict:
    """
    Perform a statistical test on the given data in a csv format.

    The function reads the data from csv, makes necessary transformations
    and ask a series of questions the user answers to perform the appropriate statistical test.

    This function is not for statistically testing regression analysis

    Returns:
    dict: A test statistic and p-value.
    """

    # Load data from csv file
    try:
        data = pd.read_csv(file_name)
    except FileNotFoundError:
        raise FileNotFoundError(f"The file {file_name} was not found in the directory.")
    except pd.errors.EmptyDataError:
        raise ValueError(f"The file {file_name} is empty.")
    except pd.errors.ParserError:
        raise ValueError(f"The file {file_name} could not be parsed. Please check the format.")

    # drop any rows with missing values
    data.dropna(inplace=True)

    # Check if the data is empty after dropping missing values
    if data.empty:
        raise ValueError("The data is empty after dropping missing values.")

    # make all columns title lower case
    data.columns = data.columns.str.strip().str.lower()

    # summarise the dataset
    data.describe(include='all')

    while True:    
            target_column = input(f"Please enter the name of the target variable column from the following (or enter 'q' to quit): {', '.join(data.columns)}: ").strip().lower()

            if target_column == 'q':
                print("Exiting the program.")
                break

            # Validate the target column
            if target_column not in data.columns:
                print(f"Invalid target column. Please choose from: {', '.join(data.columns)}")
                continue

            # Test whether the target variable is continuous or categorical
            if pd.api.types.is_numeric_dtype(data[target_column]):
                target_type = 'continuous'
                print(f"The target variable '{target_column}' is identified as {target_type}.")
                confirm = input("Is this correct? 'yes' to confirm target column / 'no' to re-enter): ").strip().lower()
                if confirm == 'no':
                    print("Please choose a different target variable column.")
                    continue
                elif confirm == 'yes':
                    print(f"The target variable '{target_column}' is confirmed as {target_type}.")
                    break
                else:
                    print("Invalid input. Please enter 'yes' or 'no'.")
                    continue
            elif pd.api.types.is_datetime64_any_dtype(data[target_column]):
                target_type = 'continuous - datetime'
                print(f"The target variable '{target_column}' is identified as {target_type}. This is not a valid target variable for statistical testing. Please choose a different column.")
                continue
            elif (pd.api.types.is_bool_dtype(data[target_column])
                or isinstance(data[target_column].dtype, pd.CategoricalDtype)
                or pd.api.types.is_object_dtype(data[target_column])
                or pd.api.types.is_string_dtype(data[target_column])):
                target_type = 'categorical'
                print(f"The target variable '{target_column}' is identified as {target_type}.")
                target_unique_values = data[target_column].unique()
                count_unique_values = len(target_unique_values)
                if count_unique_values > 15:
                    print(f"The target variable '{target_column}' is identified as {target_type} with {count_unique_values} unique values. This may not be suitable for statistical testing. Please choose a different column.")
                    continue
                else:
                    print(f"Unique values in '{target_column}': {', '.join(target_unique_values)}")
                    confirm = input("Is this correct? 'yes' to confirm target column / 'no' to re-enter): ").strip().lower()
                    if confirm == 'no':
                        print("Please choose a different target variable column.")
                        continue
                    elif confirm == 'yes':
                        print(f"The target variable '{target_column}' is confirmed as {target_type}.")
                        break
            else:
                target_type = 'unknown'
                print(f"The target variable '{target_column}' is identified as {target_type}. Please choose a different column.")
                continue

            break

    # after selecting the target column we can remove it from the list of independent columns
    independent_columns = [col for col in data.columns if col != target_column]

    while True:
        # ask the user which column the independent variable is in
        independent_column = input(f"Please enter the name of the independent variable column from the following (or enter 'q' to quit): {', '.join(independent_columns)}: ").strip().lower()

        if independent_column == 'q':
            print("Exiting the program.")
            break

        # Validate the independent column
        if independent_column not in independent_columns:
            print(f"Invalid independent column. Please choose from: {', '.join(independent_columns)}")
            continue

        # Validate that the independent variable is not the same as the target variable
        if independent_column == target_column:
            print("The independent variable cannot be the same as the target variable. Please choose a different column.")
            continue

        if pd.api.types.is_numeric_dtype(data[independent_column]):
            print("The independent variable must be categorical. Please choose a different column. If you want to use a numerical independent variable, please consider using regression analysis instead.")
            force_independant_column_category = input("Is the independant column meant to be categorical and do you want to force the independent variable to be treated as categorical? (yes/no): ").strip().lower()
            if force_independant_column_category == 'yes':
                unique_values = data[independent_column].unique()
                print(f"The unique values in the independent variable column '{independent_column}' are: {unique_values}")
                confirm_force = input("Are you sure you want to force this column to be treated as categorical? (yes/no): ").strip().lower()
                if confirm_force == 'yes':
                    data[independent_column] = data[independent_column].astype('category')
                else:
                    print("Please choose a different independent variable column.")
                    continue
                break
            else:
                continue
        elif pd.pd.types.is_datetime64_any_dtype(data[independent_column]):
            print("The independent variable must be categorical. Please choose a different column.")
            continue
        elif (pd.api.types.is_bool_dtype(column)
            or isinstance(column.dtype, pd.CategoricalDtype)
            or pd.api.types.is_object_dtype(column)
            or pd.api.types.is_string_dtype(column)
        ):
            category_unique_values = data[independent_column].unique()
            print(f"The unique values in the independent variable column '{independent_column}' are: {category_unique_values}")
            continue_test_confirmation = input("Do you want to continue with this independent variable? (yes/no): ").strip().lower()
            if continue_test_confirmation == 'yes':
                break
            else:
                print("Please choose a different independent variable column.")
                continue

    if target_type == 'continuous':
        # perform a normility test on the target variable
        print(f"Performing Shapiro-Wilk normality test on the target variable '{target_column}'...")
        print("H0: The data is normally distributed. H1: The data is not normally distributed.")
        shapiro_test_statistic, shapiro_p_value = stats.shapiro(data[target_column])
        if shapiro_p_value > 0.05:
            print(f"The p-value = {shapiro_p_value:.4f}). At a significance level of 0.05, we fail to reject the null hypothesis. The data is normally distributed.")
        else:
            print(f"The p-value = {shapiro_p_value:.4f}). At a significance level of 0.05, we reject the null hypothesis. The data is not normally distributed.")
        print(f"Here is a histogram and a Q-Q plot of the target variable '{target_column}' to visually assess normality.")
        
            





    






    
