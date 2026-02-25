# ☕ Cafe Sales Dashboard


An interactive Power BI dashboard analyzing cafe sales transactions with comprehensive insights into product performance, payment methods, locations, and temporal trends.

---

## 📊 Dashboard Overview

This Power BI report provides a complete analysis of cafe sales data, featuring:
- **KPI metrics** for quick insights
- **Temporal analysis** of sales trends
- **Product performance** tracking
- **Location-based analytics**
- **Payment method distribution**
- **Interactive filtering** capabilities

---

## 📁 Dataset Description

### **File:** `dirty_cafe_sales.csv`

### **Dataset Stats:**
- **Total Transactions:** 10,000 records
- **Date Range:** 2023 (Full year)
- **Products:** 8 main categories
- **Locations:** 2 primary types (In-store, Takeaway)
- **Payment Methods:** 3 types (Cash, Credit Card, Digital Wallet)

---

## 🗂️ Data Structure

### **Columns:**

| Column Name | Data Type | Description | Sample Values |
|-------------|-----------|-------------|---------------|
| **Transaction ID** | Text | Unique identifier for each transaction | TXN_1961373, TXN_4977031 |
| **Item** | Text | Product/item purchased | Coffee, Cake, Sandwich, Salad, etc. |
| **Quantity** | Integer | Number of items in transaction | 1-5 |
| **Price Per Unit** | Decimal | Price per single item (in currency units) | 1.0, 2.0, 3.0, 4.0, 5.0 |
| **Total Spent** | Decimal | Total transaction amount (Qty × Price) | 4.0, 12.0, 20.0 |
| **Payment Method** | Text | How customer paid | Cash, Credit Card, Digital Wallet |
| **Location** | Text | Where transaction occurred | In-store, Takeaway |
| **Transaction Date** | Date | Date of transaction | 2023-01-01 to 2023-12-31 |

---

## 🛠️ Data Quality Issues (The "Dirty" Data)

This dataset intentionally contains data quality issues for cleaning practice:

### **Issues Found:**

1. **Missing Values:**
   - ~333 records with blank Item names
   - ~2,579 records with missing Payment Method
   - ~3,265 records with missing Location
   - Some blank dates

2. **Error Values:**
   - "ERROR" appears in Item (~292 records)
   - "ERROR" appears in Payment Method (~306 records)
   - "ERROR" appears in Location (~358 records)
   - "ERROR" appears in Total Spent field
   - "ERROR" appears in Transaction Date

3. **Unknown Values:**
   - "UNKNOWN" in Item field (~344 records)
   - "UNKNOWN" in Payment Method (~293 records)
   - "UNKNOWN" in Location (~338 records)

4. **Data Inconsistencies:**
   - Some Total Spent values marked as "ERROR"
   - Mismatched calculations (Quantity × Price ≠ Total Spent in some rows)

---

## 📈 Product Distribution

| Product | Count | Percentage |
|---------|-------|------------|
| Juice | 1,171 | ~11.7% |
| Coffee | 1,165 | ~11.7% |
| Salad | 1,148 | ~11.5% |
| Cake | 1,139 | ~11.4% |
| Sandwich | 1,131 | ~11.3% |
| Smoothie | 1,096 | ~11.0% |
| Cookie | 1,092 | ~10.9% |
| Tea | 1,089 | ~10.9% |
| *Missing/Error* | 969 | ~9.7% |

---

## 💳 Payment Method Distribution

| Payment Method | Count | Percentage |
|----------------|-------|------------|
| Digital Wallet | 2,291 | ~22.9% |
| Credit Card | 2,273 | ~22.7% |
| Cash | 2,258 | ~22.6% |
| *Missing* | 2,579 | ~25.8% |
| *Error/Unknown* | 599 | ~6.0% |

---

## 📍 Location Distribution

| Location | Count | Percentage |
|----------|-------|------------|
| *Missing* | 3,265 | ~32.7% |
| Takeaway | 3,022 | ~30.2% |
| In-store | 3,017 | ~30.2% |
| *Error/Unknown* | 696 | ~7.0% |

---

## 🔧 Power BI Implementation Steps

### **1. Data Import & Connection**
- Connected to CSV file using "Get Data" → "Text/CSV"
- Loaded data into Power Query Editor

### **2. Data Cleaning & Transformation**

#### **Power Query Steps:**

**A. Replaced Error Values:**
```M
// Replace "ERROR" with null across all columns
= Table.ReplaceValue(#"Previous Step","ERROR",null,Replacer.ReplaceText,{"Item", "Payment Method", "Location", "Total Spent", "Transaction Date"})
```

**B. Replaced Unknown Values:**
```M
// Replace "UNKNOWN" with null
= Table.ReplaceValue(#"Previous Step","UNKNOWN",null,Replacer.ReplaceText,{"Item", "Payment Method", "Location"})
```

**C. Handled Blank Values:**
```M
// Replaced blank strings with null for proper handling
= Table.ReplaceValue(#"Previous Step","",null,Replacer.ReplaceValue,{"Item", "Payment Method", "Location"})
```

**D. Fixed Data Types:**
```M
// Set correct data types
= Table.TransformColumnTypes(#"Previous Step",{
    {"Transaction ID", type text},
    {"Item", type text},
    {"Quantity", Int64.Type},
    {"Price Per Unit", type number},
    {"Total Spent", type number},
    {"Payment Method", type text},
    {"Location", type text},
    {"Transaction Date", type date}
})
```

**E. Calculated Total Sales (Fixed):**
```M
// Recalculated Total Sales from Quantity × Price Per Unit
= Table.AddColumn(#"Previous Step", "Total Sales", each [Quantity] * [Price Per Unit], type number)
```

**F. Filtered Invalid Dates:**
```M
// Removed rows with invalid dates
= Table.SelectRows(#"Previous Step", each [Transaction Date] <> null and [Transaction Date] >= #date(2023,1,1) and [Transaction Date] <= #date(2023,12,31))
```

### **3. Data Model Setup**

#### **Created Dimension Tables:**

**A. DateTable (Calendar Table):**
```DAX
DateTable = 
ADDCOLUMNS(
    CALENDAR(DATE(2023,1,1), DATE(2023,12,31)),
    "Year", YEAR([Date]),
    "Month", FORMAT([Date], "MMM"),
    "MonthNum", MONTH([Date]),
    "Quarter", "Q" & FORMAT([Date], "Q"),
    "Weekday", FORMAT([Date], "dddd"),
    "Day", DAY([Date])
)
```

**B. Products Table:**
- Extracted distinct items from fact table
- Added Product_ID for relationships

**C. Locations Table:**
- Created dimension for In-store vs Takeaway
- Added Location_ID

**D. Payment_Methods Table:**
- Distinct payment types
- Added Payment_ID

#### **Created Relationships:**
- `dirty_cafe_sales[Transaction Date]` → `DateTable[Date]` (Many-to-One)
- `dirty_cafe_sales[Item]` → `Products[Item]` (Many-to-One)
- `dirty_cafe_sales[Location]` → `Locations[Location]` (Many-to-One)
- `dirty_cafe_sales[Payment Method]` → `Payment_Methods[Payment Method]` (Many-to-One)

### **4. DAX Measures Created**

```DAX
// Total Revenue
Total Sales = SUM(dirty_cafe_sales[Total Sales])

// Total Transactions
Total Transactions = COUNTROWS(dirty_cafe_sales)

// Average Order Value
Average Order Value = 
DIVIDE(
    [Total Sales],
    [Total Transactions],
    0
)

// Total Quantity Sold
Total Quantity = SUM(dirty_cafe_sales[Quantity])

// Items Per Transaction
Items Per Transaction = 
DIVIDE(
    [Total Quantity],
    [Total Transactions],
    0
)

// Distinct Items Sold
Distinct Items = DISTINCTCOUNT(dirty_cafe_sales[Item])

// Average Transaction Value
Average Transaction = 
DIVIDE(
    [Total Sales],
    [Total Transactions],
    0
)

// Price Per Unit
Price Per Unit = 
DIVIDE(
    [Total Sales],
    [Total Quantity],
    0
)

// Total Locations (Active)
Total Locations = DISTINCTCOUNT(dirty_cafe_sales[Location])

// Total Spent (Alternative name for Total Sales)
Total Spent = [Total Sales]

// Percentage of Total
% of Total Sales = 
DIVIDE(
    [Total Sales],
    CALCULATE([Total Sales], ALL(Products)),
    0
)
```

### **5. Dashboard Design**

#### **Color Theme: Cafe/Coffee Palette**
```
Header Background: #6F4E37 (Coffee Brown)
Accent Colors: #8B4513, #A0522D, #CD853F
Light Backgrounds: #F5DEB3 (Cream)
Text: #3E2723 (Dark Brown)
Highlights: #FF6F00 (Amber)
```

#### **Canvas Setup:**
- **Dimensions:** 1280 × 720 px (16:9)
- **Layout:** Header + 3 rows (KPIs, Charts, Detailed Charts)

#### **Visualizations Added:**

**Row 1 - KPI Cards (4 cards):**
1. Total Sales
2. Total Transactions  
3. Average Order Value
4. Items Per Transaction

**Row 2 - Main Insights:**
1. Insights Text Box (Key findings)
2. Orders by Day of Week (Bar Chart)
3. Sales Trend by Month (Area Chart)

**Row 3 - Detailed Analysis:**
1. Revenue by Product (Donut Chart)
2. Revenue by Location (Donut Chart)
3. Revenue by Payment Method (Donut Chart)
4. Top Products by Quantity (Bar Chart)

### **6. Formatting Applied**

- **Data Labels:** Enabled with values and percentages
- **Tooltips:** Customized with additional context
- **Sorting:** Descending by values
- **Filters:** Added slicers for Date, Product, Location
- **Interactions:** Configured cross-filtering between visuals
- **Conditional Formatting:** Applied to highlight top/bottom performers

---

## 🎯 Key Insights from Dashboard

### **Sales Performance:**
- Total revenue analysis across time periods
- Product mix and contribution to revenue
- Transaction volume trends

### **Customer Behavior:**
- Preferred payment methods
- In-store vs Takeaway preferences
- Peak transaction days/months

### **Product Analysis:**
- Best-selling items by quantity
- Revenue contribution by product
- Average price points

### **Operational Insights:**
- Busiest days for staffing optimization
- Seasonal trends for inventory planning
- Location performance comparison

---

## 📊 Dashboard Features

### **Interactive Elements:**
- ✅ Date range slicer
- ✅ Product filter
- ✅ Location filter
- ✅ Payment method filter
- ✅ Cross-visual filtering
- ✅ Drill-through capabilities
- ✅ Hover tooltips with details

### **Visual Types Used:**
- 📊 Bar Charts (comparisons & rankings)
- 🥧 Donut Charts (proportions & distribution)
- 📈 Area Charts (trends over time)
- 🔢 KPI Cards (key metrics)
- 📝 Text Boxes (insights & annotations)

---

## 🚀 How to Use This Dashboard

### **Prerequisites:**
- Power BI Desktop (free download from Microsoft)
- Windows 10 or later (or Power BI Service for cloud)

### **Steps:**

1. **Download Files:**
   ```
   - Cafe_Sales.pbix
   - dirty_cafe_sales.csv
   ```

2. **Open in Power BI:**
   - Double-click `Cafe_Sales.pbix`
   - Power BI Desktop will open automatically

3. **Refresh Data (if needed):**
   - Click "Home" → "Refresh"
   - Ensures latest data is loaded

4. **Interact with Dashboard:**
   - Click on visuals to filter
   - Use slicers to narrow focus
   - Hover for detailed tooltips

5. **Export/Share:**
   - File → Export to PDF (for presentations)
   - Publish to Power BI Service (for web sharing)

---

## 🛠️ Technical Requirements

### **Software:**
- Power BI Desktop (Latest version recommended)
- Windows 10/11 or Power BI Service

### **File Specifications:**
- `.pbix` file size: ~1-5 MB (with embedded data)
- `.csv` file size: ~500 KB (10,000 rows)

### **Skills Demonstrated:**
- Data cleaning in Power Query
- Star schema data modeling
- DAX measure creation
- Dashboard design principles
- Data visualization best practices
- Color theory application
- UX/UI considerations

---

## 📚 Learning Resources

### **Power Query Transformations:**
- Replacing values
- Handling nulls and errors
- Data type conversions
- Calculated columns

### **DAX Measures:**
- Aggregation functions (SUM, COUNT, AVERAGE)
- Iterator functions (SUMX, AVERAGEX)
- CALCULATE and filter context
- Time intelligence (if implemented)

### **Data Modeling:**
- Star schema design
- One-to-many relationships
- Dimension and fact tables
- Cardinality considerations

### **Visualization:**
- Choosing appropriate chart types
- Color psychology in dashboards
- Layout and spacing principles
- Accessibility considerations

---

## 📝 Data Cleaning Decisions

### **Why This Approach:**

1. **Replaced ERRORs with null:** Allows for proper aggregation and filtering
2. **Kept original columns:** Maintains data lineage for auditing
3. **Created calculated Total Sales:** Ensures consistency across calculations
4. **Created dimension tables:** Enables better performance and flexibility
5. **Filtered invalid dates:** Prevents skewed temporal analysis

### **Alternative Approaches Considered:**
- Could replace nulls with "Unknown" category (opted for null to show data quality issues)
- Could exclude error rows entirely (opted to keep for transparency)
- Could impute missing values (opted not to, to preserve data integrity)

---

## 🎨 Design Choices

### **Coffee Theme Rationale:**
- Aligns with cafe business domain
- Warm, inviting colors match hospitality industry
- Professional yet approachable aesthetic
- High contrast for readability

### **Layout Decisions:**
- Top row = Most important metrics (KPIs)
- Middle row = Trends and patterns
- Bottom row = Detailed breakdowns
- Left-to-right reading flow

---

## 📦 Project Structure

```
cafe-sales-dashboard/
│
├── 📄 Cafe_Sales.pbix          # Power BI report file
├── 📄 dirty_cafe_sales.csv     # Source data (with quality issues)
├── 📄 README.md                # This file
│
└── 📸 screenshots/             # (Optional) Dashboard images
    ├── overview.png
    ├── kpi_cards.png
    └── charts.png
```

---

## 🔄 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2024 | Initial dashboard creation |
| 1.1 | 2024 | Data cleaning improvements |
| 1.2 | 2024 | Added coffee color theme |
| 1.3 | 2024 | Enhanced DAX measures |

---

## 🤝 Contributing

This is a learning/portfolio project. Suggestions for improvements are welcome!

### **Potential Enhancements:**
- [ ] Add year-over-year comparison (needs multi-year data)
- [ ] Implement predictive analytics
- [ ] Add customer segmentation analysis
- [ ] Create mobile-optimized view
- [ ] Add drill-through pages for detailed analysis
- [ ] Implement row-level security (for multi-user scenarios)

---

## 📄 License

This project is available for educational and portfolio purposes.

**Data:** Sample/synthetic data for demonstration
**Report:** Free to use as template with attribution

---
---

Analysis` `Cafe` `Hospitality` `Portfolio Project`

---

**⭐ If you found this helpful, please star this repository!**

---

*Last Updated: February 2026*
