# How to find possible duplicates when using DedupliFHIR

## What are cluster_id and unique_id?
When you open a spreadsheet saved from DedupliFHIR in Microsoft Excel, you'll notice **2 new columns** not in your original file of patient data:
- **unique_id:** Identifies a specific patient record
- **cluster_id:** Identifies a cluster of possible duplicates  

DedupliFHIR identifies records about the same fundamental source of information (for example, a patient).

## Use cluster_id to find possible duplicates 
**Records with exactly the same cluster_id could be duplicates.** Below are 2 ways to view them in Excel. 

### To sort by cluster_id: 
1. Open the spreadsheet and select the cluster_id column.
2. In the “Data” menu, select "Sort.
3. In the "Sort Warning" dialog box, select "Continue with the current selection," then click the "Sort..." button.  
4. In the "Sort" menu, choose options for "Sort on" (for example, Values) and "Order" (for example, Smallest to Largest), then click the "OK" button. 
5. All rows in the spreadsheet will be sorted by cluster_id based on the sorting option you selected (for example, Smallest to Largest).

Note: If you go to "Filter" or “AutoFilter,” there are similar options for sorting. 

### To autofilter by cluster_id:
1. Open the spreadsheet and select the cluster_id column.
2. In the “Data” menu, select "Filter" or “AutoFilter.”
3. Click the arrow next to the column heading "cluster_id."
4. Select a cluster_id from the list.
5. The spreadsheet will contain only the records with the cluster_id(s) you selected.






