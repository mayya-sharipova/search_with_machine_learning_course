import fasttext
import csv

input_file = r'/workspace/datasets/fasttext/synonyms/top_words.txt'
output_file = r'/workspace/datasets/fasttext/synonyms/synonyms.csv'
model_file = r'/workspace/datasets/fasttext/synonyms/normalized_title_model.bin'
model = fasttext.load_model(model_file)

threshold = 0.75
with open(input_file, 'r') as top_words_file, open(output_file, 'w') as synonyms_file:
    csv_writer = csv.writer(synonyms_file)
    for line in top_words_file:
        word = line.strip()
        results = []
        results.append(word)
        nns = model.get_nearest_neighbors(word)
        for (sim, nn) in nns:
            if sim >= threshold:
                results.append(nn)
        print(results)

        if len(results) > 1:
            csv_writer.writerow(results)

