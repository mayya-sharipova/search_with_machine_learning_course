import os
import argparse
import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np
import csv
import re

# Useful if you want to perform stemming.
import nltk


def get_parent_cat_with_min_counts(cat, categories_by_counts, parents_df):
    if cat in categories_by_counts:
        return cat
    
    parent_ctg = parents_df.loc[parents_df['category'] == cat, 'parent'].iloc[0]
    get_parent_cat_with_min_counts(parent_ctg, categories_by_counts, parents_df)


stemmer = nltk.stem.PorterStemmer()

categories_file_name = r'/workspace/datasets/product_data/categories/categories_0001_abcat0010000_to_pcmcat99300050000.xml'

queries_file_name = r'/workspace/datasets/train.csv'
output_file_name = r'/workspace/datasets/labeled_query_data.txt'

parser = argparse.ArgumentParser(description='Process arguments.')
general = parser.add_argument_group("general")
general.add_argument("--min_queries", default=1,  help="The minimum number of queries per category label (default is 1)")
general.add_argument("--output", default=output_file_name, help="the file to output to")

args = parser.parse_args()
output_file_name = args.output

if args.min_queries:
    min_queries = int(args.min_queries)

# The root category, named Best Buy with id cat00000, doesn't have a parent.
root_category_id = 'cat00000'

tree = ET.parse(categories_file_name)
root = tree.getroot()

# Parse the category XML file to map each category id to its parent category id in a dataframe.
categories = []
parents = []
for child in root:
    id = child.find('id').text
    cat_path = child.find('path')
    cat_path_ids = [cat.find('id').text for cat in cat_path]
    leaf_id = cat_path_ids[-1]
    if leaf_id != root_category_id:
        categories.append(leaf_id)
        parents.append(cat_path_ids[-2])
parents_df = pd.DataFrame(list(zip(categories, parents)), columns =['category', 'parent'])

# Read the training data into pandas, only keeping queries with non-root categories in our category tree.
df = pd.read_csv(queries_file_name)[['category', 'query']]
df = df[df['category'].isin(categories)]

# IMPLEMENT ME: Convert queries to lowercase, and optionally implement other normalization, like stemming.
non_alpahnum_pattern = re.compile('[^a-zA-Z0-9]')
multiple_spaces_pattern = re.compile('\s+')
categories_by_counts = {}
for index, row in df.iterrows():
    query = row['query']
    # substitute non-alphanumeric characters with spaces
    normalized_query = re.sub(non_alpahnum_pattern, ' ', query)
    # substitue multiple spaces with a single spac
    normalized_query = re.sub(multiple_spaces_pattern, ' ', normalized_query)
    # lower case and stem, PorterStemmer also lowercases
    stemmed_query = stemmer.stem(normalized_query)
    df.at[index,'query'] = stemmed_query
    
    category = row['category']
    categories_by_counts[category] = categories_by_counts.get(category, 0) + 1
   


# IMPLEMENT ME: Roll up categories to ancestors to satisfy the minimum number of queries per category.
is_rolled = True
while is_rolled == True:
    is_rolled = False
    new_categories_by_counts = {}
    for ctg, cnt in categories_by_counts.items():
        new_ctg = ctg
        if cnt < min_queries:
            if ctg in parents_df['category'].unique():
                parent_ctg = parents_df.loc[parents_df['category'] == ctg, 'parent'].iloc[0]
                new_ctg = parent_ctg
                is_rolled = True
            else:
                print(ctg)
        new_categories_by_counts[new_ctg] = new_categories_by_counts.get(new_ctg, 0) + cnt
    print(len(categories_by_counts), '->', len(new_categories_by_counts))          
    categories_by_counts = new_categories_by_counts
    
df['category']= df['category'].apply(lambda cat: get_parent_cat_with_min_counts(cat, categories_by_counts, parents_df))

# Create labels in fastText format.
df['label'] = '__label__' + df['category']

# Output labeled query data as a space-separated file, making sure that every category is in the taxonomy.
df = df[df['category'].isin(categories)]
df['output'] = df['label'] + ' ' + df['query']
df[['output']].to_csv(output_file_name, header=False, sep='|', escapechar='\\', quoting=csv.QUOTE_NONE, index=False)
