def gen_number(word):
	p = inflect.engine()
	if word:
		if p.singular_noun(word) is False:
			return p.plural(word)
		else:
			return word
	else:
		return word


def gen_new_variants(data,action,obj,place):
	for variant in data:
		subs = {
			'action':[action] if action else [],
			'object':[obj] if obj else [],
			'place':[place] if place else []
		}
		offset=0
		newvar = copy.deepcopy(variant)
		for entity in newvar['entities']:
			try:
				value = subs[entity['entity'].lower()].pop()
				diff = len(value) - len(entity['value'])
				start = offset + entity['start']
				end = offset + entity['end']
				newvar['text'] = newvar['text'][:start] + value + newvar['text'][end:]
				entity['value'] = value
				entity['start'] = entity['start'] + offset
				offset += diff
				entity['end'] = entity['end'] + offset
			except (IndexError, KeyError) as exc:
				entity['start'] += offset
				entity['end'] += offset
				continue
		yield newvar


if __name__ == "__main__":
	from gen_base import get_variants
	import sys
	import argparse
	import copy
	import itertools
	import json
	import inflect

	
	CLI=argparse.ArgumentParser()
	
	CLI.add_argument("--oauth_token",nargs="?",type=str,default="tokenprovidedbybitext",required=True,help="Your oauth_token provided by Bitext")
	CLI.add_argument("--sentence",nargs="?",type=str,default="",help="The sentence from which you want to generate the variants for the intent.")
	CLI.add_argument("--intent_name",nargs="?",type=str,default="",required=True,help="The intent name")
	CLI.add_argument("--mode",nargs="?",type=str,default="generic",required=True,help="mode: generic,home")
	CLI.add_argument("--politeness",nargs="?",type=int,default=0,help="Add politeness to variants")
	CLI.add_argument("--negation",nargs="?",type=int,default=0,help="Add negation to variants")
	CLI.add_argument("--number",nargs="?",type=int,default=0,help="Add number to var")
	CLI.add_argument("--action",nargs="+",default=[],help="A list of actions")
	CLI.add_argument("--object",nargs="+",default=[],help="A list of objects")
	CLI.add_argument("--place",nargs="+",default=[],help="A list of places")
	CLI.add_argument("-o", "--output", help="Directs the output to a file")
	CLI.add_argument("-f",'--infile', default="")
	args = CLI.parse_args()	
	
	if args.infile and args.sentence:
		print('You can not provide the program with a seed phrase file and a seed phrase on the CLI at the same time')
		sys.exit()
	# If a file with seed sentences is provided, gen a base json with the variants of all seeds
	if args.infile:
		with open(args.infile, 'w') as f:
			data = f.readlines()
			base = {"rasa_nlu_data": {"common_examples": []}}
			for x in data:
				base_json = get_variants(args.oauth_token, x, args.intent_name, args.mode, bool(args.politeness),bool(args.negation))
				base['rasa_nlu_data']['common_examples'].extend(base_json['rasa_nlu_data']['common_examples'])
			base_json = base
	# If a seed sentence is provided via CLI
	if args.sentence:
		base_json = get_variants(args.oauth_token, args.sentence, args.intent_name, args.mode, bool(args.politeness),bool(args.negation),bool(args.number))
	# Parse the lists of entities and add a None value to each
	if args.action or args.object or args.place:

		if len(args.action) == 1:
			action = args.action[0].split(",")
			action.append(None)
		elif len(args.action) > 1:
			action = args.action
			action.append(None)
		else:
			action = [None]
		
		if len(args.object) <= 1:
			objects = args.object[0].split(",")
			objects.append(None)
		elif len(args.object) > 1:
			objects = args.object
			objects.append(None)
		else:
			object = []
		
		if len(args.place) <= 1:
			place = args.place[0].split(",")
			place.append(None)
		elif len(args.place) > 1:
			place = args.place
			place.append(None)
		else:
			place = []

		if args.number:
			new_object = []
			new_place = []
			for o in objects:
				if o: new_object.append(gen_number(o))
			objects.extend(new_object)
			for p in place:
				if p: new_place.append(gen_number(p))
			place.extend(new_place)
	
			# Gen the variants of all posible combinations from the lists of entities with number
			to_append_json = []
			rtexts=[]
			for lista in itertools.product(*[action, objects, place]):
				result = []
				for x in gen_new_variants(base_json['rasa_nlu_data']['common_examples'],lista[0],lista[1],lista[2]):
					if x["text"] not in rtexts:
						result.append(x)
						rtexts.append(x["text"])
				to_append_json.extend(result)
			"""
			for lista in itertools.product(*[action, new_object, new_place]):
				result = []
				for x in gen_new_variants(base_json['rasa_nlu_data']['common_examples'],lista[0],lista[1],lista[2]):
					if x["text"] not in rtexts:
						result.append(x)
						rtexts.append(x["text"])
				to_append_json.extend(result)
			"""
		else:
			# Gen the variants of all posible combinations from the lists of entities
			to_append_json = []
			rtexts=[]

			for lista in itertools.product(*[action, objects, place]):
				result = []
				for x in gen_new_variants(base_json['rasa_nlu_data']['common_examples'],lista[0],lista[1],lista[2]):
					if x["text"] not in rtexts:
						result.append(x)
						rtexts.append(x["text"])
				to_append_json.extend(result)

		
		#Extend de base json with the new variants
		final_json = {'rasa_nlu_data': {'common_examples': []}}
		final_json['rasa_nlu_data']['common_examples'].extend(to_append_json)

		if args.output:
			# Write out the results to a file
			with open(args.output, 'w') as output_file:
				json.dump(final_json, output_file, indent=4)
		else:
			print(json.dumps(final_json,indent=4))

