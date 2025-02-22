import pandas as pd
import re
import os

path= input ("enter file path to csv:")
cleaned_input = path.strip('"\'')
file_path = input("enter destination path and file name:")
cleaned_file = file_path.strip('"\'')

df = pd.read_csv(f"{cleaned_input}")

# #finds rows where pattern matches and extracts stack number and suture quantity
def extract_picked(message):
    match = re.findall(r'(\"quantity\":\s*[^"]*,\s*\"stackNumber\":\s*"[^"]*"),\s*"barcode":\s*"[^"]*",\s*"status":\s*"picked"'
    , message, re.IGNORECASE)
    if match:
        return match
    return None

# # #creates column with stack numbers and quantities and removes
# rows that did not have status as picked
df['pick_info'] = df['message_content'].apply(extract_picked)
df_cleaned = df.dropna(subset=['pick_info'])
# #Flatten the list of lists into a single list
all_numbers = [num for sublist in df_cleaned['pick_info'] for num in sublist]
df_picked = pd.DataFrame(all_numbers)
df_picked.columns=['info']
# #separates quantity and stack into separate columns
df_picked['picked quantity'] = df_picked['info'].str.extract(r'"quantity":\s*(\d+)').astype(int)
df_picked['Stack number'] = df_picked['info'].str.extract(r'"stackNumber":\s*"(\d+)"')

#groups by stack number and sums suture quantities for each stack number
df_grouped_picked = df_picked.groupby('Stack number')['picked quantity'].sum().reset_index()
# #finds rows where pattern matches and extracts stack number and suture quantity
def extract_unreadable(message):
    match = re.findall(r'(\"quantity\":\s*[^"]*,\s*\"stackNumber\":\s*"[^"]*"),\s*"barcode":\s*"[^"]*",\s*"status":\s*"Unreadable"'
    , message, re.IGNORECASE)
    if match:
        return match
    return None

# #creates column with pick stack numbers and quantities and removes
#rows that did not have status as unreadable
df['pick_info'] = df['message_content'].apply(extract_unreadable)
df_cleaned = df.dropna(subset=['pick_info'])
# #Flatten the list of lists into a single list
all_numbers = [num for sublist in df_cleaned['pick_info'] for num in sublist]
df_unreadable = pd.DataFrame(all_numbers)

df_unreadable.columns=['info']
# #separates quantity and stack into separate columns
df_unreadable['unreadable quantity'] = df_unreadable['info'].str.extract(r'"quantity":\s*(\d+)').astype(int)
df_unreadable['stack number'] = df_unreadable['info'].str.extract(r'"stackNumber":\s*"(\d+)"')

#groups by stack number and sums suture quantities for each stack number
df_grouped_unreadable = df_unreadable.groupby('stack number')['unreadable quantity'].sum().reset_index()
#
def extract_suction(message):
    match = re.findall(r'Low\s*suction\s*pressure\s*detected\s*while\s*picking\s*from\s*(\d+)'
    , message, re.IGNORECASE)
    if match:
        return match
    return None

# # #creates column with pick stack numbers and quantities and removes rows that didn't have suction loss
df['pick_info'] = df['message_content'].apply(extract_suction)
df_cleaned = df.dropna(subset=['pick_info'])
# #Flatten the list of lists into a single list
all_numbers = [num for sublist in df_cleaned['pick_info'] for num in sublist]

value_counts = pd.Series(all_numbers).value_counts()
value_counts_df = value_counts.reset_index() #creates data frame with only stack numbers and their occurance count
value_counts_df.columns = ['Stack Number', 'Suction Loss quantity']  # Rename columns
#groups by stack number and adds suture quantities for each stack number group
df_grouped_suction = value_counts_df.groupby('Stack Number')['Suction Loss quantity'].sum().reset_index()
df_concat = pd.concat([df_grouped_picked, df_grouped_unreadable, df_grouped_suction], axis=1)
df_concat.to_csv(f"{cleaned_file}.csv", index=False)
