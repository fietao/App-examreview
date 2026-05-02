import re
with open('study_app.py', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()
print('MC:', content.count('"type":"mc"'))
print('TF:', content.count('"type":"tf"'))
print('FTE:', content.count('"type":"fte"'))
print('AW:', content.count('"type":"aw"'))
print('SA:', content.count('"type":"sa"'))
