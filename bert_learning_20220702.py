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
text = '明日の天気は晴れだ。'
encoding = tokenizer(text, max_length=12, padding='max_length',truncation=True)
print('# encoding')
print(encoding)
tokens = tokenizer.convert_ids_to_tokens(encoding['input_ids'])
print('# tokens')
print(tokens)
