# Statistical Outlier Detection System using Z-Score

A beginner-friendly college project that finds outliers in a list of numbers.

| Part | Technology | Job |
|------|-----------|-----|
| Frontend | HTML, CSS, JavaScript | Input form, summary cards, graph, table |
| Backend | Python Flask | Validates input, runs C++ and the plot script, returns results |
| Computation | C++ | **All** statistics: mean, standard deviation, Z-Scores, classification, CSV |
| Graph | Python Matplotlib | Reads the CSV and draws the scatter plot |

---

## 1. Objective

To build a system that takes a dataset, calculates a Z-Score for every value, and
detects **outliers** (values unusually far from the rest of the data) using the rule **|Z| > 3**.

## 2. Z-Score Formula

```
Z = (X - Mean) / Standard Deviation
```

- **X** – the data value
- **Mean** = (x1 + x2 + ... + xn) / n
- **Population Standard Deviation** = sqrt( [ (x1-Mean)² + ... + (xn-Mean)² ] / n )

The Z-Score says *how many standard deviations a value is away from the mean*.
If `|Z| > 3` the value is classified as an **Outlier**, otherwise **Normal**.

## 3. Methodology (workflow)

```
Browser (script.js)
   │  1. User types numbers, clicks Analyze  → POST /analyze
   ▼
Flask (app.py)
   │  2. Validates input (numbers only, at least 2, no empty items)
   │  3. Sends the numbers to the C++ program
   ▼
C++ (src/outlier.cpp)
   │  4. Mean → Standard Deviation → Z-Scores → Normal/Outlier
   │  5. Saves output/results.csv and prints a short summary
   ▼
Matplotlib (scripts/plot.py)
   │  6. Reads results.csv and saves static/plot.png
   ▼
Flask → Browser
      7. Browser shows the cards, graph and results table
```

**Edge cases handled**
- Empty input, text instead of numbers, empty items (`1,,2`), `nan`/`inf`, fewer than 2 values, huge numbers → friendly error message.
- **Standard deviation = 0** (all values equal): dividing by zero is impossible, so C++ sets every Z-Score to 0, reports no outliers, and the page shows an explanation.

## 4. Project structure

```
outlier-detector/
├── app.py               Flask backend
├── requirements.txt     Python packages (Flask, matplotlib)
├── src/outlier.cpp      C++ calculations
├── scripts/plot.py      Matplotlib graph
├── templates/index.html Web page
├── static/style.css     Styling
├── static/script.js     Frontend logic
└── output/              results.csv is created here
```

## 5. Setup and run on macOS

**Step 1 – Install the C++ compiler** (skip if `g++ --version` already works):
```bash
xcode-select --install
```

**Step 2 – Open the project folder in Terminal:**
```bash
cd path/to/outlier-detector
```

**Step 3 – Create a virtual environment and install packages:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Step 4 – (Optional) Compile the C++ program yourself.**
`app.py` does this automatically on first run, but you can also do it manually:
```bash
g++ -o src/outlier src/outlier.cpp
```

**Step 5 – Start the server:**
```bash
python app.py
```

**Step 6 – Open the app** in your browser: **http://127.0.0.1:5001**

> Port 5001 is used because macOS reserves port 5000 for AirPlay Receiver.
> Press `Ctrl + C` in Terminal to stop the server.

## 6. Test with the sample dataset

Click **Sample data**, then **Analyze**. Dataset:
`10, 12, 11, 13, 12, 14, 13, 15, 12, 11, 14, 13, 100`

Expected result (verified):

| Mean | Std Dev | Observations | Outliers |
|------|---------|--------------|----------|
| 19.2308 | 23.3540 | 13 | 1 |

The value **100** has Z = **3.4585**, which is greater than 3, so it is an **Outlier**.
All other values have Z-Scores between -0.40 and -0.18 (Normal).

## 7. Real-world applications

- **Banking** – spotting unusual transactions that may be fraud
- **Healthcare** – detecting abnormal test results or sensor readings
- **Manufacturing** – finding defective products with measurements far from the norm
- **Education** – identifying unusually high or low exam scores
- **Data cleaning** – removing typing errors before analysis or machine learning
- **Network security** – noticing sudden spikes in traffic

## 8. Viva questions and simple answers

**Q1. What is an outlier?**
A value that is very different from most of the other values in the dataset.

**Q2. What is a Z-Score?**
It tells how many standard deviations a value is above or below the mean. Formula: `Z = (X - Mean) / SD`.

**Q3. Why do we use the threshold 3?**
In a normal (bell-shaped) distribution about 99.7% of values lie within 3 standard deviations of the mean. A value outside that range is very rare, so we call it an outlier.

**Q4. What does a Z-Score of 0 mean?**
The value is exactly equal to the mean.

**Q5. What does a negative Z-Score mean?**
The value is below the mean. A positive Z-Score means it is above the mean.

**Q6. What is the difference between population and sample standard deviation?**
Population SD divides by *n*; sample SD divides by *n − 1*. This project uses the population SD because we treat the entered numbers as the complete dataset.

**Q7. What happens if the standard deviation is 0?**
All values are the same, so there is nothing unusual. Dividing by 0 is not allowed, so the program sets every Z-Score to 0 and reports no outliers.

**Q8. Why is C++ used for the calculations?**
C++ is fast and shows the mathematics clearly with simple loops and functions. Python (Flask) only connects the parts and Matplotlib only draws the graph.

**Q9. How does Flask talk to C++?**
Flask runs the compiled C++ program using Python's `subprocess` module, sends the numbers through standard input, and reads the summary from standard output.

**Q10. How does the graph know which points are outliers?**
C++ writes a `status` column ("Normal" or "Outlier") in the CSV. Matplotlib reads that column and colors outliers red.

**Q11. Why did 100 become an outlier in the sample data?**
The other values are close to 10-15, but 100 is far away. Its Z-Score is 3.46, which is more than 3.

**Q12. What are the limitations of the Z-Score method?**
- Outliers themselves increase the mean and standard deviation, which can hide them ("masking").
- It works best for roughly bell-shaped data.
- In small datasets the rule `|Z| > 3` can never trigger: the largest possible |Z| with population SD is √(n − 1), so you need at least **11 values** before any value can be flagged.
# CM_PROJECT
