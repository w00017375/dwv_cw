The project represents the environment for data analyzes with the dataframe uploading, cleaning, analyzes that consequently the result can be exported. The app is developed through the Streamlit framework, so the main purpose is to optimize and standardize the process of data preprocessing before modeling and data analysis.

Functionality
1. Data Uploading
Modified dataframe can be exported in several formats (CSV, Excel or JSON). After uploading the brief overview of dataset will be showcased, including:
•	Amount of rows and columns
•	Data type
•	Amount of missed values
•	Amount of duplicates
2. Data Cleaning
The section aims to transform the data. The implementation completes following aspects:
•	Handling missing values
o	Filling null values with mean, median and mode values
o	Filling null values with previous and next values
o	Filling null values with user input values
o	Deleting rows with missed values
•	Duplicates handling through deleting either full rows deleting or subset of rows
•	Data type transforming
•	Outliers handling - IQR and percentiles settling
•	Scaling, including Min-Max normalization and Z-score standardization
After each operation the result of data manipulation is shown to the user in the fragment overview of the updated dataframe.
3. Visualization
A user can build different visualization types based on the dataframe such as
•	Histogram
•	Boxplot
•	Scatter plot
•	Line chart
•	Bar chart
•	Correlation matrixes
Also filters by categories and numeric values are available in the section.
4. Export and Report
The results of dataframe transforming can be exported in CSV, Excel and JSON formats for the next data manipulations or in the format of recipe with the data transformation step chronology.

The project is completed through using the pandas and numpy libraries within the Streamlit interface that is controlled by using session_state control. All operations are completed without affecting the original file of the dataframe, ensuring the integrity of backup file.

