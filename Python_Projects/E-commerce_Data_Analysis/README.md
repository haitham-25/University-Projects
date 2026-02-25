# E-Commerce Data Analysis & Customer Segmentation Project

## 📊 Project Overview

This comprehensive data analysis project demonstrates end-to-end data science workflows on an e-commerce retail dataset. The project encompasses data cleaning, exploratory data analysis, feature engineering, statistical testing, dimensionality reduction, and customer segmentation using unsupervised learning techniques.

**Key Focus Areas:**
- Retail transaction analysis and revenue optimization
- Customer behavior patterns and segmentation
- Product performance analytics
- Statistical hypothesis testing
- Machine learning for clustering

## 🎯 Business Objectives

1. **Revenue Analysis**: Identify key revenue drivers and high-value transactions
2. **Customer Insights**: Segment customers based on purchasing behavior
3. **Product Performance**: Determine top-performing products and return patterns
4. **Seasonal Trends**: Uncover temporal patterns in sales data
5. **Geographic Analysis**: Analyze revenue distribution across different countries

## 📁 Dataset

The dataset contains transactional data from an online retail store, including:
- **Invoice details**: Transaction IDs and dates
- **Product information**: Stock codes, descriptions, quantities, and unit prices
- **Customer data**: Customer IDs and country information
- **Calculated metrics**: Revenue per transaction
- **Data source**: https://www.kaggle.com/datasets/carrie1/ecommerce-data

## 🛠️ Technologies & Libraries

```python
- pandas & numpy: Data manipulation and numerical computations
- matplotlib & seaborn: Statistical data visualization
- plotly: Interactive visualizations
- scikit-learn: Machine learning algorithms (PCA, Clustering, Feature Selection)
- scipy: Statistical testing and probability distributions
```

## 📈 Project Workflow

### 1. Data Wrangling & Cleaning

**Missing Values Handling**
- Identified and analyzed missing data patterns
- Applied appropriate imputation strategies

**Duplicate Detection & Removal**
- Identified and removed duplicate transactions
- Ensured data integrity

**Outlier Detection & Treatment**
- Applied IQR (Interquartile Range) method for outlier detection
- Handled outliers in Quantity, UnitPrice, and Revenue columns
- Used clipping and removal strategies based on business context

**Return Transaction Processing**
- Created `IsReturn` column to flag negative quantity transactions
- Separated returns from regular transactions for specialized analysis

**Data Type Conversions**
- Standardized date formats
- Converted string columns to appropriate numeric types
- Removed invalid characters from price fields

### 2. Exploratory Data Analysis (EDA)

#### Univariate Analysis
- Revenue distribution analysis
- Identification of maximum and minimum revenue transactions
- Top and bottom performing products

#### Multivariate Analysis
- **Quantity vs Revenue**: Correlation analysis between order size and revenue
- **UnitPrice vs Revenue**: Price sensitivity analysis
- **Country vs Revenue**: Geographic revenue distribution
- **Product Analysis**: Top-selling and highest revenue-generating products

#### Customer Behavior Analysis
- Top customers by revenue contribution
- Customer purchase frequency patterns
- Average basket size analysis

#### Temporal Analysis
- **Seasonality Patterns**: Monthly and quarterly trends
- **Day of Week Analysis**: Revenue patterns across weekdays
- **Time Series Trends**: Sales evolution over time

#### Product Analytics
- Products with high return rates
- Frequently ordered products
- Product bundle analysis (frequently bought together)
- Average basket size by product

#### Correlation Analysis
- Comprehensive correlation heatmap
- Feature relationship exploration

### 3. Feature Engineering & Selection

**New Feature Creation**
- Derived meaningful features from existing data
- Enhanced dataset with business-relevant metrics

**Feature Selection Techniques**
- **Filter Methods**: Correlation-based feature selection
- **Lasso Regularization**: L1 penalty for feature importance
- **RFE (Recursive Feature Elimination)**: Iterative feature selection
- Selected optimal feature subset for modeling

### 4. Statistical Analysis

#### Probability Calculations
- P(Revenue > 10): Likelihood of high-value transactions
- P(UK Customers): Geographic distribution probabilities
- P(Return): Return rate probability
- P(Non-UK): International customer probability
- P(Quantity > 5): Bulk order probability

#### Distribution Fitting
- Revenue distribution modeling
- Best-fit distribution identification

#### Hypothesis Testing
- **Chi-Square Test**: Relationship between returns and country
- Statistical significance testing for business insights
- P-value interpretation for decision-making

### 5. Dimensionality Reduction (PCA)

- Principal Component Analysis implementation
- Feature space reduction while preserving variance
- Visualization of principal components
- Explained variance ratio analysis

### 6. Customer Segmentation (Clustering)

- Unsupervised learning for customer grouping
- Cluster analysis and interpretation
- Customer segment profiling
- Business recommendations based on segments

## 🔍 Key Insights & Findings

- Identified distinct customer segments with varying purchasing behaviors
- Discovered seasonal patterns affecting revenue
- Highlighted top revenue-generating products and customers
- Quantified return rates and identified problematic products
- Geographic analysis revealed high-potential markets

## 📊 Visualizations

The project includes comprehensive visualizations:
- Distribution plots and histograms
- Scatter plots for relationship analysis
- Heatmaps for correlation matrices
- Time series plots for temporal trends
- Bar charts for comparative analysis
- Interactive Plotly visualizations

## 🚀 How to Run

## 💡 Skills Demonstrated

- **Data Cleaning**: Comprehensive data wrangling and preprocessing
- **Statistical Analysis**: Probability theory and hypothesis testing
- **Exploratory Data Analysis(EDA)**: In-depth pattern discovery
- **Feature Engineering**: Creating valuable features from raw data
- **Machine Learning**: Dimensionality reduction and clustering
- **Data Visualization**: Clear and insightful visual communication
- **Business Analytics**: Translating data insights into business value

## 📚 Project Structure

```
├── Data_Analysis_Final_Project_.ipynb    # Main analysis notebook
├── README.md                              # Project documentation
└── [data/]:(https://www.kaggle.com/datasets/carrie1/ecommerce-data)                                  # Dataset (if included)
```

## 🎓 Learning Outcomes

This project showcases practical application of:
- End-to-end data analysis pipeline
- Statistical rigor in data science
- Business problem-solving using analytics
- Communication of technical findings

## 📫 Contact

Feel free to reach out for questions or collaboration opportunities!

- **LinkedIn**: [www.linkedin.com/in/mohamedmahdy206]
- **GitHub**: [https://github.com/mahdy206]
- **Email**: [mmahdy935@gmail.com]
- **Portfolio**: [https://mahdy206.github.io/]

*This project was completed as part of [Data Analysis Course] demonstrating comprehensive data analysis and machine learning skills.*