import sys
import os
import json


base_path = os.path.dirname(os.path.abspath(__file__))
base = {'rasa_nlu_data': {'common_examples': []}}
for x in sys.argv[1:]:
	with open(x) as f:
		data = json.load(f)
		base['rasa_nlu_data']['common_examples'].extend(data['rasa_nlu_data']['common_examples'])

with open(os.path.join(base_path,'data/training_data.json'), 'w') as d:
	json.dump(base,d)
