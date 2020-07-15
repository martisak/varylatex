# Based on this example on DecisionTrees with scikit learn :
# http://chrisstrelioff.ws/sandbox/2015/06/08/decision_trees_in_python_with_scikit_learn_and_pandas.html
# Basic imports
import os
import subprocess

# Data manipulation imports
from sklearn.tree import DecisionTreeClassifier, export_graphviz
import pandas as pd


def visualize_tree(tree, feature_names, output_path):
    dot_path = os.path.join(output_path, "dt.dot")
    img_path = os.path.join(output_path, "dt.png")
    with open(dot_path, 'w') as f:
        export_graphviz(tree, out_file=f,
                        feature_names=feature_names,
                        filled=True,
                        special_characters=True,
                        rounded=True,
                        class_names=list(map(str,tree.classes_)))
    command = ["dot", "-Tpng", dot_path, "-o", img_path]
    try:
        subprocess.check_call(command)
    except subprocess.CalledProcessError:
        exit("Could not run dot, ie graphviz, to "
             "produce visualization")


def load_csv(csv_path):
    """
    Creates a dataframe based on the CSV path
    """
    return pd.read_csv(csv_path, index_col = 0)


def refine_csv(df):
    """
    Transforms the categorical values (typically strings) of the sets into integers that could
    be exploited by the DecisionTree
    """
    # Set of categorical values
    cat_vals = set()

    # Change string (seen as objects) values to booleans
    for col_name, col_type in dict(df.dtypes).items():
        if col_type == 'O':  # If this is a column of objects (true for strings)
            df = pd.concat([df, pd.get_dummies(df[col_name], prefix=col_name)], axis=1)
            cat_vals.add(col_name)

    # Get all the features except the class (nbPages), the remaining space, and initial categorical features
    features = list(set(df.columns) - set(["nbPages", "space"]) - cat_vals)

    return df, features


def get_sample_size(df, perc):
    """
    The size of the training set based on a percentage of the total dataframe
    """
    return int(len(df)*float(perc)/100)


def split_frame(df, features, sample):
    """
    Separates the dataframe into training and testing set and gives the results for every entry
    """
    y = df["nbPages"]
    train = df[features][:sample]
    test = df[features][sample:]
    return train, test, y


def create_dt(train, y, sample, min_samples_split=10, random_state=99):
    dt = DecisionTreeClassifier(min_samples_split=min_samples_split, random_state=random_state)
    dt.fit(train, y[:sample])
    return dt


def decision_tree(csv_path, perc=100, output_path=None):
    df = load_csv(csv_path)
    # Replace string values by booleans with one-hot method
    df, features = refine_csv(df)
    # Get the training sample size
    sample = get_sample_size(df, perc)
    # Separate the data
    train, test, y = split_frame(df, features, sample)
    # Create the Decision Tree classifier
    dt = create_dt(train, y, sample, min_samples_split=4)
    
    # Only useful for testing, but we may use 100% of the data for training, and skip the computing of the accuracy
    if perc < 100:
        print("Accuracy :", dt.score(test, y[sample:]))

    # Generate a .dot and a .png file of the tree if there is an output path
    if output_path:
        visualize_tree(dt, features, output_path)

    return dt
