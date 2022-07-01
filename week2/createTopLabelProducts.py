import argparse


parser = argparse.ArgumentParser()
parser.add_argument("min_count", help="minimum number of products in a category for it to be selected", type=int)
args = parser.parse_args()
min_count = args.min_count

input_file = r'/workspace/datasets/fasttext/labeled_products.txt'
output_file = r'/workspace/datasets/fasttext/pruned_labeled_products.txt'

print("Finding top labels with at least %s products" % min_count)
categories_by_count = {}

with open(input_file, 'r') as products_file:
    for line in products_file:
        category = line.split()[0]
        if category in categories_by_count:
            categories_by_count[category] += 1
        else:
            categories_by_count[category] = 1

top_categories = []
for ctgr, cnt in categories_by_count.items():
    if cnt >= min_count:
        top_categories.append(ctgr)
        print(ctgr, ' : ', cnt)

print("\nWriting results to %s" % output_file)
with open(input_file, 'r') as products_file, open(output_file, 'w') as pruned_products_file:
    for line in products_file:
        category = line.split()[0]
        if category in top_categories:
            pruned_products_file.write(line)
