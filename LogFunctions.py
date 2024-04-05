import pandas as pd
import os
import matplotlib.pyplot as plt
def LogDeploymentResults(portfolioValue: float, endDate: str) -> None:
    script_directory = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(script_directory, "Resources/BacktestResults.txt")

    with open(data_file, "a") as f:
        f.write(f"{portfolioValue},{endDate}\n")
        f.close()
def LoadLogs() -> None:
    script_directory = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(script_directory, "Resources/BacktestResults.txt")
    log = pd.read_csv(data_file, sep=",",names=["TotalValue", "TransactionDate"])
    log["TransactionDate"].apply(lambda x: x.split(" ")[0])
    log.plot(x="TransactionDate")
    plt.show(block=True)


if __name__ == "__main__":
    LoadLogs()
