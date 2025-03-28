import numpy as np
import pandas as pd
from metrics import average_dicts

def save_summary_tables(dataset_name, model_name,
                        accuracies_train_dict, accuracies_test_dict,
                        train_subpop_dict, test_subpop_dict,
                        mia_overall_dict, mia_subpop_dict,
                        fairness_metrics_dict, output_dir="new_results"):
    """
    Saves three summary tables as CSV files:
      1. Merged Accuracies (overall and subpopulations)
      2. Merged MIA results (overall and subgroup)
      3. Merged Fairness metrics

    All inputs are dictionaries with experiment names as keys.
    """
    # Overall accuracies
    overall_acc_df = pd.DataFrame({
        key: [np.mean(val)] for key, val in accuracies_train_dict.items()
    }, index=["Overall Train Accuracy"])
    overall_acc_df_test = pd.DataFrame({
        key: [np.mean(val)] for key, val in accuracies_test_dict.items()
    }, index=["Overall Test Accuracy"])
    overall_acc = pd.concat([overall_acc_df, overall_acc_df_test], axis=0)
    
    # Subpopulation accuracies
    train_subpop_df = pd.DataFrame({key: average_dicts(val) for key, val in train_subpop_dict.items()})
    train_subpop_df.index = ["Train: " + str(idx) for idx in train_subpop_df.index]
    test_subpop_df = pd.DataFrame({key: average_dicts(val) for key, val in test_subpop_dict.items()})
    test_subpop_df.index = ["Test: " + str(idx) for idx in test_subpop_df.index]
    
    accuracies_df = pd.concat([overall_acc, train_subpop_df, test_subpop_df], axis=0)
    accuracies_df.index.name = "Accuracy Metric"
    accuracies_df.to_csv(f"{output_dir}/lira_train_test_accuracies/lira_{dataset_name}_{model_name}_train_test_accuracies.csv")
    
    # MIA results
    mia_overall_df = pd.DataFrame(mia_overall_dict, index=["Overall MIA"])
    mia_subpop_df = pd.DataFrame(mia_subpop_dict)
    mia_subpop_df.index.name = "Subpopulation"
    mia_df = pd.concat([mia_overall_df, mia_subpop_df], axis=0)
    mia_df.to_csv(f"{output_dir}/lira_mia_results/lira_{dataset_name}_{model_name}_mia.csv")
    
    # Fairness metrics
    fairness_df = pd.DataFrame({key: average_dicts(val) for key, val in fairness_metrics_dict.items()})
    fairness_df.index.name = "Fairness Metric"
    fairness_df.to_csv(f"{output_dir}/lira_fairness/lira_{dataset_name}_{model_name}_fairness.csv")
    
    return {
        'accuracies': accuracies_df,
        'mia': mia_df,
        'fairness': fairness_df
    }