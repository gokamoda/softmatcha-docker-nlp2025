
source .venv/bin/activate

# Japanese

python src/preprocess/merge_txts.py \
    data/txt/ja/*.txt \
    data/txt/NLP2025_ja.txt
python src/indexing.py \
    --backend fasttext \
    --model fasttext-ja-vectors \
    --index data/fasttext-ja-vectors_nlp2025.h5 \
    --num_workers 16 \
    --buffer_size 10000 \
    --chunk_size 1024 \
    data/txt/NLP2025_ja.txt


# English Wikitext, 0.1B, glove-wiki-gigaword-300
python src/preprocess/merge_txts.py \
    data/txt/en/*.txt \
    data/txt/NLP2025_en.txt
 python src/indexing.py \
    --backend gensim \
    --model glove-wiki-gigaword-300 \
    --index data/glove-wiki-gigaword-300_nlp2025.h5 \
    --num_workers 16 \
    --buffer_size 10000 \
    --chunk_size 1024 \
    data/txt/NLP2025_en.txt

