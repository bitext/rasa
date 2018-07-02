import requests
import json

def get_variants(token, sent, intent, mode='home', politeness=False, negation=False, all_numbers=False):
	
	output_json = []
	# Building the POST request to rewriting analysis endpoint
	endpoint = "https://svc02.api.bitext.com/variants/"
	headers = {"Authorization": "bearer " + token, "Content-Type": "application/json"}
	header = {"Authorization": "bearer " + token}
	params = {"language": "eng", "mode": mode, "text": sent, "intent": intent, \
			"politeness": politeness, "negation": negation, "all_numbers": all_numbers, "output": "rasa"}
	
	# Sending the POST request
	res = requests.post(endpoint, headers=headers, data=json.dumps(params))
	
	# Processing the result of the POST request
	post_result = json.loads(res.text).get('success')   # Success of the request
	post_result_code = res.status_code                  # Error code, if applicable
	post_msg = json.loads(res.text).get('message')      # Error message, if applicable
	action_id = json.loads(res.text).get('resultid')    # Identifier to request the analysis results
	
	print("POST: '" + post_msg + "'\n\n")
	
	# 401 is the error code corresponding to an invalid token
	if post_result_code == 401:
		print("Your authentication token is not correct\n")
	
	if (post_result):
		print("Waiting for generation results for sentence: " + '"' + sent + '"' + "...\n\n")
	
		# GET request loop, using the response identifier returned in the POST answer
		analysis = None
		while analysis == None:
			res = requests.get(endpoint + action_id + '/', headers=headers)
			if res.status_code == 200:
				analysis = json.loads(res.text)
	
		# The list will have more than one index if the text is composed of different sentences.
		for item in analysis["utterances"]:
			output_json.extend(item)
	
		# The loop ends when we have response to the GET request
		get_msg = res.reason
		print("GET: '" + get_msg + "'\n\n")

	with open('original_nlu.json','w+') as f:
		json.dump(output_json,f,indent=4)

	return {"rasa_nlu_data": {"common_examples": output_json}}
