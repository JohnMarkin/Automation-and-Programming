#!/usr/bin/env python
# coding: utf-8

# In[1]:


## Loading Packages

import pandas as pd
import numpy as np
from datetime import datetime
import time
import math 
import statistics
import calendar
from tkinter import Tk
from tkinter.filedialog import askopenfilename


# In[42]:


## Loading Packages

import pandas as pd
import numpy as np
from datetime import datetime
import time
import math 
import statistics
import calendar
from tkinter import Tk
from tkinter.filedialog import askopenfilename


class VM22_Calculator:

    # Initialize the VM22 Calculation by providing Inputs
    def __init__(self, year_input=None, quarter_input=None):
        if year_input is None:
            year_input = int(input("Enter the year: "))
            
        if quarter_input is None:
            quarter_input = int(input("Enter the quarter (e.g., 1): "))
        
        self.year = int(year_input)
        self.quarter = int(quarter_input)
        
        #Load Files 

        # Hide the root window
        Tk().withdraw()

        # Open file dialog to select CSV file
        treasury_path = askopenfilename(title="Select a Treasury file CSV", filetypes=[("CSV files", "*.csv")])
        tablex_path = askopenfilename(title="Select a TableX file CSV Note the Formating", filetypes=[("CSV files", "*.csv")])
        tableA_path = askopenfilename(title="Select a Table A Default file CSV Note the Formating", filetypes=[("CSV files", "*.csv")])
        refweights_path = askopenfilename(title="Select CSV Weights for Reference Rate file", filetypes=[("CSV files", "*.csv")])
        spread_path = askopenfilename(title="Select CSV Weights for Spread file", filetypes=[("CSV files", "*.csv")])
        defcosts_path = askopenfilename(title="Select CSV Weights for Defualt Cost file. If VM Quarter to be calculated falls in Q1 or Q2 utilise the Table A from VM22 Year - 2 else -1", filetypes=[("CSV files", "*.csv")])
        dailycorp_path = askopenfilename(title="Selec CSV  Daily Corporate Rate file", filetypes=[("CSV files", "*.csv")])

        # Read CSV file into a DataFrame
        treasury = pd.read_csv(treasury_path)
        treasury = treasury.sort_values(by="Date", ascending=True)
        treasury['Date'] = pd.to_datetime(treasury['Date'])# Ensure the 'Date' column is in datetime format

        # Apply the function to create the new 'quarter' column
        treasury['Quarter'] = treasury['Date'].apply(self.get_quarter)
        self.treasury = treasury
        
        #Weigths
        refweights = pd.read_csv(refweights_path)
        self.refweights = refweights

        spreadw = pd.read_csv(spread_path)
        self.spreadw = spreadw

        defcostsw = pd.read_csv(defcosts_path)
        self.defcostsw = defcostsw

        dailycorpsw = pd.read_csv(dailycorp_path)
        self.dailycorpsw =dailycorpsw

        tablex = pd.read_csv(tablex_path)
        self.tablex = tablex
        
        tableA = pd.read_csv(tableA_path)
        self.tableA = tableA

        #Prescribed Portfolio Credit Quality Distribution
        pre_credit_dist = pd.Series({'Aaa': 0.0, 'Aa': 0.15, 'A': 0.4, 'Baa': 0.4})
        self.pre_credit_dist = pre_credit_dist
        
        VM22Period = str(year_input) + "Q"  + str(quarter_input)
        self.VM22Period = VM22Period

        if quarter_input == 1:
            VM22RefP =str(year_input) + "Q"  + str(4)
            self.VM22RefP = VM22RefP
        else:
            VM22RefP =str(year_input) + "Q"  + str(quarter_input - 1)
            self.VM22RefP = VM22RefP
        
        # Convert percentage strings to floats
        for col in ['2 Year', '5 Year', '10 Year']:
            self.defcostsw[col] = self.defcostsw[col].str.rstrip('%').astype(float) / 100
            
        # Convert percentage strings to floats
        for col in ['2 Year', '5 Year', '10 Year', '30 Year']:
            self.spreadw[col] = self.spreadw[col].str.rstrip('%').astype(float) / 100

        
     # Define a function to determine the quarter string
    def get_quarter(self,date):
            year = date.year
            month = date.month
            if 1 <= month <= 3:
                quarter = 'Q1'
            elif 4 <= month <= 6:
                quarter = 'Q2'
            elif 7 <= month <= 9:
                quarter = 'Q3'
            else:
                quarter = 'Q4'
            return f"{year}{quarter}"

        
        
        

    def reference_rate(self):
        
        # Reference Rate Calc
        # Compute the Quarterly Treasury Rate: 

        ## Group by 'quarter' and compute the mean of each numeric column
        quarterly_all = self.treasury.groupby('Quarter').mean(numeric_only=True).reset_index()
        selected_columns = ['Quarter','2 Yr', '5 Yr', '10 Yr', '30 Yr']
        quarterly_avg = quarterly_all[selected_columns].copy()
        quarterly_avg = quarterly_avg.round(2)

        # Find the weighted Average of Quarterly Rates and the Reference Weights Section 3 Part D
        q_columns = [col for col in quarterly_avg.columns if col != 'Quarter']
        ref_columns = [col for col in self.refweights.columns if col != 'Bucket']
        for col in ref_columns:
            self.refweights[col] = self.refweights[col].astype(str).str.rstrip('%').astype(float) / 100

        # List to store results
        results = []

        # Loop through each row in quarterly_avg
        for _, i in quarterly_avg.iterrows():

                if i[0] == self.VM22RefP:
                    quarter = i['Quarter']
                    vec1 = i[q_columns].values.astype(float)

                    # Loop through each row in table2
                    for _, j in self.refweights.iterrows():
                        bucket = j['Bucket']
                        vec2 = j[ref_columns].values.astype(float)

                        # Compute dot product
                        dot_product = (vec1 * vec2).sum()

                        # Store the result
                        results.append({
                            'Quarter': self.VM22Period,
                            'Bucket': bucket,
                            'Reference Rates': dot_product

                })


        # Convert results to a DataFrame
        Ref_Rates = pd.DataFrame(results)
    
        return Ref_Rates
    
    
    
    def spread_rate(self):
        
        #Compute Spread 

        sub_tablex = self.tablex[self.tablex['WAL'].isin([2, 5, 10, 30])]
        final_tablex = pd.DataFrame()
        final_tablex['Quarter']= sub_tablex['Quarter']
        final_tablex['WAL'] =sub_tablex['WAL']
        # Create new averaged columns
        final_tablex['Aaa'] = sub_tablex['Aaa/AAA']

        final_tablex['Aa'] = sub_tablex[['Aa1/AA+', 'Aa2/AA', 'Aa3/AA-']].mean(axis=1)
        final_tablex['A'] = sub_tablex[['A1/A+', 'A2/A', 'A3/A-']].mean(axis=1)
        final_tablex['Baa'] = sub_tablex[['Baa1/BBB+', 'Baa2/BBB', 'Baa3/BBB-']].mean(axis=1)

        # Compute weighted average using dot product
        final_tablex['WeightedAverage'] = final_tablex[self.pre_credit_dist.index].dot(self.pre_credit_dist)


        # Compute rates
        results = []
        for quarter in final_tablex['Quarter'].unique():
            
            if quarter == self.VM22Period:
                sub = final_tablex[final_tablex['Quarter'] == quarter]
                for _, row in self.spreadw.iterrows():
                    spread = (
                        row['2 Year'] * sub[sub['WAL'] == 2]['WeightedAverage'].values[0] +
                        row['5 Year'] * sub[sub['WAL'] == 5]['WeightedAverage'].values[0] +
                        row['10 Year'] * sub[sub['WAL'] == 10]['WeightedAverage'].values[0] +
                        row['30 Year'] * sub[sub['WAL'] == 30]['WeightedAverage'].values[0]
                    )/10000
                    results.append({
                        'Quarter': quarter,
                        'Bucket': row['Bucket'],
                        'Spread Rate': round(spread, 8)
                    })

        # Final table
        Spreads = pd.DataFrame(results)

        return Spreads
    

    def default_cost(self):
        #Compute Default Cost 
        # Updated only  in June
        # Convert percentage strings to floats
        

        # Define groupings
        groups = {
            'Aaa': ['Aaa'],
            'Aa': ['Aa1', 'Aa2', 'Aa3'],
            'A': ['A1', 'A2', 'A3'],
            'Baa': ['Baa1', 'Baa2', 'Baa3']
        }

        # Columns to include
        cols_to_avg = ['2', '5', '10']

        # Build the summary table
        summary = {}
        for rating_group, ratings in groups.items():
            group_df = self.tableA[self.tableA["Moody's Credit Rating"].isin(ratings)]
            summary[rating_group] = group_df[cols_to_avg].mean().round(2)

        # Convert to DataFrame
        summary_df = pd.DataFrame(summary).T
        summary_df.index.name = "Moody's Credit Rating"
        summary_df.columns = [2, 5, 10]
        summary_df = summary_df.T
        summary_df['WeightedAverage'] = summary_df[self.pre_credit_dist.index].dot(self.pre_credit_dist)

        # Compute rates
        results = []
        for _, row in self.defcostsw.iterrows():
            dcost = (
                    row['2 Year'] * summary_df[summary_df.index == 2]['WeightedAverage'].values[0]+
                    row['5 Year'] * summary_df[summary_df.index == 5]['WeightedAverage'].values[0] +
                    row['10 Year'] * summary_df[summary_df.index == 10]['WeightedAverage'].values[0] 
                    )/10000
            results.append({ 'Bucket': row['Bucket'], 'Default Cost': round(dcost, 6)})

        # Final table
        DefCosts = pd.DataFrame(results)
        
        return DefCosts 

        
    def VM22_Rates(self):
        Ref = self.reference_rate()
        Def = self.default_cost()
        spread = self.spread_rate()
        Answer = (Ref["Reference Rates"] + spread["Spread Rate"] - Def['Default Cost'] - (0.25/100))*4
        Final_Rates = pd.DataFrame()
        Final_Rates["Quarter"] = Ref["Quarter"]
        Final_Rates["Bucket"] = Ref["Bucket"]
        Final_Rates["VM22 Quarterly Rates"] = (Answer.round(2))/4
        
        return Final_Rates
        
    


# In[46]:


VM22 = VM22_Calculator()
print(VM22.reference_rate())
print(VM22.default_cost())
print(VM22.spread_rate())
VM22.VM22_Rates()

