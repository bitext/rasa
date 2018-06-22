# Bitext Variant generation + Rasa NLU

How to build a great chatbot integrating Bitext Variant Generation and Rasa NLU.<br>
Currently we cover three vertical: Smart Home, e-commerce and news.

## Getting Started

The first thing you need to do to be able to integrate the Variants Generation service is to sign up for the [Bitext's API](https://api.bitext.com/#/login/), as you will need an oauth_token. The API has a free trial of 5000 requests.<br>Of course, you can also use the already trained model, which is in the **projects/** folder and give it a try!


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

### Generating training data with Bitext Varian Generation

Suppose you want to make a bot for a smart home, which is the example we have chosen for this demo. If we want our bot can turn on and turn off the lights of the house, we will need training data for these two intents and of course we will want to execute these intents to different objects and in different places.

Use **nlg_training.py** script to generate variants:
Variants for the intent **"turn-on"** and the entities: objects:[light,lamp...], places:[kitchen,bedroom...]
```
python3 nlg_training.py \
--oauth_token "tokenprovidedbybitext" \
--sentence "turn on the lights in the kitchen" \
--intent_name "turn on" \
--action "turn on" \
--object "light,lamp" \
--place "kitchen,badroom,bedroom,garage,garden,yard,living room,dining room,balcony,terrace,basement,attic" \
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
--action "turn off" \
--object "light,lamp" \
--place "kitchen,badroom,bedroom,garage,garden,yard,living room,dining room,balcony,terrace,basement,attic" \
--negation 1 \
--politeness 1 \
--number 0 \
-o turn_off.json
```

**Command line params:**
* Required params
  * oauth_token: Token provided by bitext
  * sentence or infile: a seed sentence or a text file with one seed sentence per line
  * intent_name: intent name
* Optional params (1-2-3)
  * action: the action or list of actions (coma separated) to apply
  * object: the object or list of objects (coma separated) to apply
  * place: the place or list of places (coma separated) to apply
* Aditional params
  * negation: add negative variants
  * politeness: add polite variants
  * number: add (plural and singular) variants
  * o: output file name

Use **join_intents.py** to generate the final training data file for Rasa. This file will be placed in **data/** directory.
```
python3 join_intents.py turn_on.json turn_off.json
```

The output should be a json file (named training_data.json) with **Rasa** format.

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

Create a file called config_spacy.yml in **config/** directory.

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
curl -X POST localhost:5000/parse -d '{"q":"Would you mind turn on the lights in the kitchen?"}' | python -m json.tool
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
      "end": 22,
      "value": "turn on",
      "confidence": 0.9999798259210771,
      "extractor": "ner_crf",
      "entity": "Action"
    },
    {
      "start": 27,
      "end": 32,
      "value": "light",
      "confidence": 0.9597315110679535,
      "extractor": "ner_crf",
      "entity": "Object"
    },
    {
      "start": 40,
      "end": 46,
      "value": "garden",
      "confidence": 0.9995846283672174,
      "extractor": "ner_crf",
      "entity": "Place"
    }
  ],
  "text": "Would you mind turn on the light of the garden?",
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
You can take a look at our test [here](https://blog.bitext.com/improving-rasas-results-with-artificial-training-data-ii)

