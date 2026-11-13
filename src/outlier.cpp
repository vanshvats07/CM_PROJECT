// ============================================================
//  Statistical Outlier Detection using Z-Score  (C++ part)
//
//  This program does ALL the statistics:
//    1. Reads numbers from standard input (sent by Flask)
//    2. Calculates the mean
//    3. Calculates the population standard deviation
//    4. Calculates the Z-score of every value
//    5. Marks each value as "Normal" or "Outlier"
//    6. Saves the results to a CSV file
//    7. Prints a short summary (key=value lines) for Flask to read
//
//  Usage:  ./outlier <path-to-output-csv>   (numbers come from stdin)
// ============================================================

#include <iostream>
#include <fstream>
#include <vector>
#include <cmath>
#include <string>
#include <iomanip>

using namespace std;

// A value is an outlier if |Z| is greater than this number
const double THRESHOLD = 3.0;

// ------------------------------------------------------------
// Mean = (x1 + x2 + ... + xn) / n
// ------------------------------------------------------------
double calculateMean(const vector<double>& values) {
    double sum = 0.0;
    for (int i = 0; i < (int)values.size(); i++) {
        sum = sum + values[i];
    }
    return sum / values.size();
}

// ------------------------------------------------------------
// Population Standard Deviation
//   variance = [ (x1-mean)^2 + (x2-mean)^2 + ... + (xn-mean)^2 ] / n
//   std dev  = square root of variance
// "Population" means we divide by n (not n-1).
// ------------------------------------------------------------
double calculateStdDev(const vector<double>& values, double mean) {
    double sumOfSquares = 0.0;
    for (int i = 0; i < (int)values.size(); i++) {
        double difference = values[i] - mean;          // (x - mean)
        sumOfSquares = sumOfSquares + difference * difference;  // (x - mean)^2
    }
    double variance = sumOfSquares / values.size();    // divide by n
    return sqrt(variance);
}

// ------------------------------------------------------------
// Z-Score:  Z = (X - Mean) / Standard Deviation
// It tells us how many standard deviations X is away from the mean.
// If the standard deviation is 0 (all values equal), we cannot divide
// by zero, so we return 0 (every value is exactly at the mean).
// ------------------------------------------------------------
double calculateZScore(double x, double mean, double stdDev) {
    if (stdDev == 0.0) {
        return 0.0;
    }
    return (x - mean) / stdDev;
}

// ------------------------------------------------------------
// Classification rule:  |Z| > 3  ->  Outlier,  otherwise Normal
// ------------------------------------------------------------
string classify(double zScore) {
    if (fabs(zScore) > THRESHOLD) {
        return "Outlier";
    }
    return "Normal";
}

int main(int argc, char* argv[]) {
    // We need the CSV path from Flask
    if (argc < 2) {
        cerr << "Missing output file path." << endl;
        return 1;
    }
    string csvPath = argv[1];

    // ---- Step 1: read all numbers from standard input ----
    vector<double> values;
    double number;
    while (cin >> number) {
        values.push_back(number);
    }

    // If reading stopped before the end of input, something was not a number
    if (!cin.eof()) {
        cerr << "Input contains a value that is not a number." << endl;
        return 1;
    }
    if (values.size() < 2) {
        cerr << "At least 2 values are required." << endl;
        return 1;
    }

    // ---- Step 2: mean and standard deviation ----
    double mean = calculateMean(values);
    double stdDev = calculateStdDev(values, mean);

    // ---- Step 3: open the CSV file ----
    ofstream csvFile(csvPath);
    if (!csvFile) {
        cerr << "Could not create the CSV file." << endl;
        return 1;
    }
    csvFile << "index,value,z_score,status" << endl;

    // ---- Step 4: Z-score + classification for every value ----
    int outlierCount = 0;
    for (int i = 0; i < (int)values.size(); i++) {
        double z = calculateZScore(values[i], mean, stdDev);
        string status = classify(z);

        if (status == "Outlier") {
            outlierCount++;
        }

        // defaultfloat keeps the value as typed (e.g. 12, not 12.0000)
        // fixed + setprecision(4) shows the Z-score with 4 decimals
        csvFile << (i + 1) << ","
                << defaultfloat << setprecision(10) << values[i] << ","
                << fixed << setprecision(4) << z << ","
                << status << endl;
    }
    csvFile.close();

    // ---- Step 5: print summary for Flask (one key=value per line) ----
    // Limits of the "normal" zone: mean - 3*SD  and  mean + 3*SD
    double lowerLimit = mean - THRESHOLD * stdDev;
    double upperLimit = mean + THRESHOLD * stdDev;

    cout << fixed << setprecision(4);
    cout << "count=" << values.size() << endl;
    cout << "mean=" << mean << endl;
    cout << "std=" << stdDev << endl;
    cout << "outliers=" << outlierCount << endl;
    cout << "lower_limit=" << lowerLimit << endl;
    cout << "upper_limit=" << upperLimit << endl;
    cout << "zero_std=" << (stdDev == 0.0 ? 1 : 0) << endl;

    return 0;
}
