# Bitext Variant generation + Rasa NLU

How to build a smart chatbot integrating Bitext Variant Generation and Rasa NLU.<br>
We currently cover three business verticals: smart home, e-commerce and news.

## Getting Started

The first thing you need to do to be able to integrate the Variant Generation service is to sign up for the [Bitext API](https://api.bitext.com/#/login/), and obtain your API Token. The API offers a **free trial with 5000 requests.**<br>You can also try the the already-trained model available in the **projects** folder.


### Installing Rasa NLU

Install Rasa NLU

```
$ pip install rasa_nlu
```

Install Spacy

```
$ pip install rasa_nlu[spacy]
$ python -m spacy download en_core_web_md
$ python -m spacy link en_core_web_md en
```

### Generating training data with Bitext Variant Generation

Suppose you want to make a bot for a smart home, which is the example we have chosen for this demo. If we wanted to have our bot turn on and turn off the lights of the house, we would need training data for these two intents with variations for different objects and places.

Use the **nlg_training.py** script to generate variants:
Variants for the intent **"turn-on"** and the entities: objects:[light,lamp...], places:[kitchen,bedroom...]
```
python3 nlg_training.py \
--oauth_token "tokenprovidedbybitext" \
--sentence "turn on the lights in the kitchen" \
--intent_name "turn on" \
--mode "home" \
--action "turn on" \
--object "light,lamp" \
--place "kitchen,bathroom,bedroom,garage,garden,yard,living room,dining room,balcony,terrace,basement,attic" \
--negation 1 \
--politeness 1 \
--number 0 \
-o turn_on.json
```

Variants for the intent **"turn-off"** and the entities: objects:[light,lamp...], places:[kitchen,bedroom...]
```
python3 nlg_training.py \
--oauth_token "tokenprovidedbybitext" \
--sentence "turn off the lights in the kitchen" \
--intent_name "turn off" \
--mode "home" \
--action "turn off" \
--object "light,lamp" \
--place "kitchen,badroom,bedroom,garage,garden,yard,living room,dining room,balcony,terrace,basement,attic" \
--negation 1 \
--politeness 1 \
--number 0 \
-o turn_off.json
```

**Command line parameters:**
* Required parameters
  * oauth_token: Token provided by Bitext
  * sentence or file: a seed sentence or a text file with one seed sentence per line
  * intent_name: intent name
  * mode: generic (news,e-commerce), home (smart home)
* Optional parameters (1-2-3)
  * action: the action or list of actions (comma-separated) to apply
  * object: the object or list of objects (comma-separated) to apply
  * place: the place or list of places (comma-separated) to apply
* Aditional parameters
  * negation: add negative variants
  * politeness: add polite variants
  * number: add (plural and singular) variants
  * o: output file name

Use **join_intents.py** to generate the final training data file for Rasa. This file will be placed in the **data** directory.
```
python3 join_intents.py turn_on.json turn_off.json
```

You should obtain a JSON file (called training_data.json) with **Rasa** format.<br>The generated training file for this example contains 8,424 utterances.

```
{
	"rasa_nlu_data": {
		"common_examples": [
			{
				"intent": "turn on",
				"text": "turn on the light in the kitchen",
				"entities": [
					{
						"start": 0,
						"value": "turn on",
						"entity": "Action",
						"end": 7
					},
					{
						"start": 12,
						"value": "light",
						"entity": "Object",
						"end": 17
					},
					{
						"start": 25,
						"value": "kitchen",
						"entity": "Place",
						"end": 32
					}
				]
			},
			...
		]
	}
}
```

### Rasa config file

Create a file called config_spacy.yml in the **config** directory.

```
language: "en"

pipeline: "spacy_sklearn"
```

### Train a spacy model

```
python -m rasa_nlu.train \
    --config config/config_spacy.yml \
    --data data/training_data.json \
    --path projects
```

### Test your model

Use Rasa NLU as a HTTP server
```
python -m rasa_nlu.server --path projects
```
Send a query
```
curl -X POST localhost:5000/parse -d '{"q":"Would you mind turning on the lights in the kitchen?"}' | python -m json.tool
```
Output should look like this
```
{
  "model": "model_20180622-231242",
  "intent": {
    "confidence": 0.9999995114650161,
    "name": "turn on"
  },
  "entities": [
    {
      "start": 15,
      "end": 25,
      "value": "turning on",
      "confidence": 0.9999798259210771,
      "extractor": "ner_crf",
      "entity": "Action"
    },
    {
      "start": 30,
      "end": 36,
      "value": "lights",
      "confidence": 0.9597315110679535,
      "extractor": "ner_crf",
      "entity": "Object"
    },
    {
      "start": 40,
      "end": 51,
      "value": "kitchen",
      "confidence": 0.9995846283672174,
      "extractor": "ner_crf",
      "entity": "Place"
    }
  ],
  "text": "Would you mind turning on the lights in the kitchen?",
  "project": "default",
  "intent_ranking": [
    {
      "confidence": 0.9999995114650161,
      "name": "turn on"
    },
    {
      "confidence": 4.885349839439467e-07,
      "name": "turn off"
    }
  ]
}
```

### Improving Rasa's results by 30% with artificial training data
You can take a look at our tests [here](https://blog.bitext.com/improving-rasas-results-with-artificial-training-data-ii)

