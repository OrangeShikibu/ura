import torch
from transformers import BertJapaneseTokenizer, BertModel
model_name = 'cl-tohoku/bert-base-japanese-whole-word-masking'
tokenizer = BertJapaneseTokenizer.from_pretrained(model_name)
tokenizer.tokenize('明日は自然言語処理の勉強をしよう。')
tokenizer.tokenize('明日はマシンラーニングの勉強をしよう。')
tokenizer.tokenize('機械学習を中国語にすると机器学濈')
input_ids = tokenizer.encode('明日は自然言語処理の勉強をしよう。')
print(input_ids)
tokenizer.convert_ids_to_tokens(input_ids)
