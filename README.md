# 🛒 Association Rule Mining & Market Basket Recommendation Demo

## 📌 Description

This project is an interactive demo of **association rule mining** applied to **market basket analysis**: finding which products tend to be bought together. All three classic frequent-itemset algorithms, **Apriori**, **FP-Growth** and **ECLAT**, are implemented from scratch in pure Python (standard library only), and a **Streamlit** web app lets you explore every step: frequent itemsets, generated rules, and "frequently bought together" recommendations for a shopping cart.

It was built as a companion demo for a term paper on association rule mining techniques. The core logic in `arm_core.py` has no third-party dependencies, so the algorithms can be read and tested on their own.

## 🚀 Features

**Algorithms (`arm_core.py`)**
- Apriori with candidate generation and pruning
- FP-Growth with FP-tree construction and conditional pattern bases
- ECLAT with vertical transaction-ID lists
- Rule generation from frequent itemsets using minimum confidence
- Product recommendation for a given cart
- Built-in self-check that verifies all three algorithms agree

**Interactive app (`app_goi_y_mua_kem.py`)**
- Data tab: item frequency overview and data preview
- Frequent itemsets tab: Apriori candidate log (`C1: 6 → L1: 4`, ...) and a text view of the FP-tree
- Rules tab: sortable table with support, confidence and lift, plus a filter to hide rules with lift ≤ 1
- Recommendation tab: build a cart and get suggested items
- Speed comparison tab: run and time all three algorithms on the current dataset
- Adjustable `minsup` and `minconf` thresholds
- Data source: built-in example, simulated dataset, or your own CSV upload

## 🧠 Key Concepts

| Metric | Meaning |
|---|---|
| **Support** of X | Fraction of transactions that contain itemset X |
| **Confidence** of X → Y | Support(X ∪ Y) / Support(X): how often Y appears when X is bought |
| **Lift** of X → Y | Confidence / Support(Y): above 1 means a positive association, below 1 means a negative one |

High confidence alone can be misleading. For example, the rule `{Beer} → {Milk}` can have confidence 0.80 yet lift 0.96, meaning milk is no more likely with beer than in general. The lift filter in the app exposes this.

## 🔑 Demo Scenarios

| Scenario | Settings | What to observe |
|---|---|---|
| **1. Correctness check** | Source: *Chapter 3 example (6 transactions)*, minsup = 0.50, minconf = 0.70 | 10 frequent itemsets and 11 rules, identical across Apriori, FP-Growth and ECLAT |
| **2. Pruning** | Algorithm: Apriori, tab *Frequent itemsets* | How candidates are cut down at each level (C3 has only 2 candidates) |
| **3. FP-tree** | Algorithm: FP-Growth | Text rendering of the FP-tree |
| **4. Confidence trap** | Tab *Rules*, sort by confidence, enable *lift > 1* | `{Beer} → {Milk}` disappears |
| **5. Recommendations** | Source: *Simulated data*, minsup ≈ 0.08, minconf 0.50, tab *Recommendations* | Adding "Diapers" suggests "Baby formula" and "Baby wipes" |
| **6. Speed** | Tab *Speed comparison*, click **Run** | Measured timings for the three algorithms on this dataset |

## 📥 Input Format

Upload a CSV from the sidebar. Two layouts are accepted:

**Layout A: two columns (one row per item in an invoice)**

```csv
InvoiceNo,Item
INV001,Bread
INV001,Milk
INV002,Beer
```

**Layout B: one transaction per line, items separated by commas**

```
Bread, Milk
Beer, Diapers, Eggs
```

## 🛠️ Technologies Used

- Python 3.9+
- Streamlit (web interface)
- pandas (data handling)
- Pure Python standard library (algorithms)

## 📂 Project Structure

```
market-basket-association-rules/
│
├── app_goi_y_mua_kem.py          # Streamlit app: data, itemsets, rules, recommendations, speed
├── arm_core.py                   # Apriori, FP-Growth, ECLAT, rule generation, recommendations
├── tao_du_lieu_mo_phong.py       # Generator for the simulated transaction dataset
├── du_lieu_mo_phong.csv          # 365 simulated transactions over 20 items
├── requirements.txt              # Python dependencies
│
├── demo_tongquan.png             # Screenshot: overview
├── demo_luat.png                 # Screenshot: rules
└── demo_goiy.png                 # Screenshot: recommendations
```

## ▶️ How to Run

**1. Clone the repository**

```bash
git clone https://github.com/giapchithanh06/market-basket-association-rules.git
cd market-basket-association-rules
```

**2. Install dependencies** (Python 3.9 or newer)

```bash
pip install -r requirements.txt
```

**3. Start the app**

```bash
streamlit run app_goi_y_mua_kem.py
```

The browser opens automatically at `http://localhost:8501`.

**4. Verify the algorithms (optional)**

```bash
python arm_core.py
```

Expected output: Apriori, FP-Growth and ECLAT each return **10 frequent itemsets** and **11 rules** with minsup = 0.5 and minconf = 0.7.

**5. Regenerate the simulated data (optional)**

```bash
python tao_du_lieu_mo_phong.py
```

The generator uses a fixed random seed, so the output is reproducible.

## ⚠️ About the Data

`du_lieu_mo_phong.csv` is **randomly generated** by `tao_du_lieu_mo_phong.py`. It is not real retail data. Co-purchase groups are planted into the generator so the algorithms have patterns to find, which makes the interface easy to demonstrate.

For real experiments, use the **Online Retail** dataset from the UCI Machine Learning Repository (Chen, 2015; doi:10.24432/C5BW33; 541,909 records; CC BY 4.0). Preprocess it, export the result to CSV, and upload it in the app.

## 🔮 Future Improvements

- Run the algorithms on the Online Retail dataset and report benchmark results
- Add unit tests for each algorithm
- Export rules to CSV
- Support sequential pattern mining over time-stamped transactions
- Add a product-level view with item names and prices

## 📚 References

- R. Agrawal, R. Srikant, "Fast Algorithms for Mining Association Rules", *VLDB*, 1994, pp. 487–499.
- J. Han, J. Pei, Y. Yin, "Mining Frequent Patterns without Candidate Generation", *SIGMOD*, 2000. [doi:10.1145/342009.335372](https://doi.org/10.1145/342009.335372)
- M. J. Zaki, "Scalable Algorithms for Association Mining", *IEEE TKDE*, 12(3), 2000, pp. 372–390. [doi:10.1109/69.846291](https://doi.org/10.1109/69.846291)
- Chen, D. (2015). Online Retail [Dataset]. UCI Machine Learning Repository. [doi:10.24432/C5BW33](https://doi.org/10.24432/C5BW33)

## 👨‍💻 Authors

**Giáp Chí Thanh**

Student Project: Association Rule Mining Demo, Software Engineering, Ho Chi Minh City University of Industry and Trade (HUIT).

GitHub: [@giapchithanh06](https://github.com/giapchithanh06) · Email: chithanhgiap0409@gmail.com

## 📄 License

This project is intended for educational and learning purposes only.
