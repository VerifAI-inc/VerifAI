import numpy as np
import pandas as pd

def average_dicts(dict_list):
    """Given a list of dictionaries, return a Series with the average for each key."""
    return pd.DataFrame(dict_list).mean()

def save_summary_tables(dataset,
                        accuracies_train_orig, accuracies_test_orig,
                        accuracies_train_syn, accuracies_test_syn,
                        train_accuracies_syn_target, test_accuracies_syn_target,
                        accuracies_train_dir, accuracies_test_dir,
                        train_accuracies_rew, test_accuracies_rew,
                        accuracies_train_egr, accuracies_test_egr,
                        train_subpop_orig, test_subpop_orig,
                        train_subpop_syn, test_subpop_syn,
                        train_subpop_syn_target, test_subpop_syn_target,
                        train_subpop_dir, test_subpop_dir,
                        train_subpop_rew, test_subpop_rew,
                        train_subpop_egr, test_subpop_egr,
                        mia_orig, mia_syn, mia_syn_target, mia_dir, mia_rew, mia_egr,
                        results_mia_subpop_orig, results_mia_subpop_syn, subgroup_means_syn_target,
                        results_mia_subpop_dir, results_mia_subpop_rew, results_mia_subpop_egr,
                        all_metrics_orig, all_metrics_syn, all_metrics_syn_target,
                        all_metrics_dir, all_metrics_rew, all_metrics_egr):
    """
    Merges and saves three summary tables as CSV files:
      1. Merged Accuracies
      2. Merged MIA results
      3. Merged Fairness metrics
      
    Returns a dictionary with the file paths of the saved CSVs.
    """
    output_files = {}
    # 1. Merged Accuracies Table
    overall_acc = {
        "orig": [np.mean(accuracies_train_orig), np.mean(accuracies_test_orig)],
        "syn": [np.mean(accuracies_train_syn), np.mean(accuracies_test_syn)],
        "syn_target": [np.mean(train_accuracies_syn_target), np.mean(test_accuracies_syn_target)],
        "dir": [np.mean(accuracies_train_dir), np.mean(accuracies_test_dir)],
        "rew": [np.mean(train_accuracies_rew), np.mean(test_accuracies_rew)],
        "egr": [np.mean(accuracies_train_egr), np.mean(accuracies_test_egr)]
    }
    overall_acc_df = pd.DataFrame(overall_acc, index=["Overall Train Accuracy", "Overall Test Accuracy"])
    
    train_subpop_agg = {
        "orig": average_dicts(train_subpop_orig),
        "syn": average_dicts(train_subpop_syn),
        "syn_target": average_dicts(train_subpop_syn_target),
        "dir": average_dicts(train_subpop_dir),
        "rew": average_dicts(train_subpop_rew),
        "egr": average_dicts(train_subpop_egr)
    }
    train_subpop_df = pd.DataFrame(train_subpop_agg)
    train_subpop_df.index = ["Train: " + str(idx) for idx in train_subpop_df.index]
    
    test_subpop_agg = {
        "orig": average_dicts(test_subpop_orig),
        "syn": average_dicts(test_subpop_syn),
        "syn_target": average_dicts(test_subpop_syn_target),
        "dir": average_dicts(test_subpop_dir),
        "rew": average_dicts(test_subpop_rew),
        "egr": average_dicts(test_subpop_egr)
    }
    test_subpop_df = pd.DataFrame(test_subpop_agg)
    test_subpop_df.index = ["Test: " + str(idx) for idx in test_subpop_df.index]
    
    accuracies_df = pd.concat([overall_acc_df, train_subpop_df, test_subpop_df], axis=0)
    accuracies_df.index.name = "Accuracy Metric"
    acc_file = f"new_results/lira_train_test_accuracies/lira_{dataset}_train_test_accuracies.csv"
    accuracies_df.to_csv(acc_file)
    output_files["accuracies"] = acc_file
    
    # 2. Merged MIA Table
    mia_overall = {
        "orig": mia_orig,
        "syn": mia_syn,
        "syn_target": mia_syn_target,
        "dir": mia_dir,
        "rew": mia_rew,
        "egr": mia_egr
    }
    mia_overall_df = pd.DataFrame(mia_overall, index=["Overall MIA"])
    
    mia_subpop_dict = {
        "orig": results_mia_subpop_orig,
        "syn": results_mia_subpop_syn,
        "syn_target": subgroup_means_syn_target,
        "dir": results_mia_subpop_dir,
        "rew": results_mia_subpop_rew,
        "egr": results_mia_subpop_egr
    }
    mia_subpop_df = pd.DataFrame(mia_subpop_dict)
    mia_subpop_df.index.name = "Subpopulation"
    
    mia_df = pd.concat([mia_overall_df, mia_subpop_df], axis=0)
    mia_file = f"new_results/lira_mia_results/lira_{dataset}_mia.csv"
    mia_df.to_csv(mia_file)
    output_files["mia"] = mia_file
    
    # 3. Merged Fairness Table
    fairness_agg = {
        "orig": average_dicts(all_metrics_orig),
        "syn": average_dicts(all_metrics_syn),
        "syn_target": average_dicts(all_metrics_syn_target),
        "dir": average_dicts(all_metrics_dir),
        "rew": average_dicts(all_metrics_rew),
        "egr": average_dicts(all_metrics_egr)
    }
    fairness_df = pd.DataFrame(fairness_agg)
    fairness_df.index.name = "Fairness Metric"
    fairness_file = f"new_results/lira_fairness/lira_{dataset}_fairness.csv"
    fairness_df.to_csv(fairness_file)
    output_files["fairness"] = fairness_file
    
    return output_files
