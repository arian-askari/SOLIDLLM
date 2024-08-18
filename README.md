# Solid Conversation

A Python library for generating intent-aware dialogues using large language models. More details are available on (https://arxiv.org/abs/2402.11633)[paper] and its (https://github.com/arian-askari/solid)[corresponding repo].

## Installation

- Clone the code.
- ```cd SOLID_CONV```
- ``` pip install -e . ```



## Usage

```python
import pprint
from solid_conversation import ConversationGenerator

entity_name = "Jönköping"
entity_type = "City"
entity_description = ("Jönköping (Swedish pronunciation: [jœnˈøːnpɪŋ] (listen)) is a city in southern Sweden, situated by the western shore of Lake Vättern. "
                      "It is the seat of Jönköping municipality and Jämtland County, and has a population of 114,418 (2019). Jönköping is part of the Swedish province "
                      "of Småland. Historically, the city has been significant due to its location at the transition between the provinces of Västergötland and Småland, "
                      "which is reflected in its architecture and cultural heritage.")
sequence_of_intents = ['OQ', 'RQ', 'FD_NF', 'PA']
conversation_starter = "How has the cultural and architectural heritage of both Västergötland and Småland influenced the development of Jönköping as a unique city?"
solid_generated_dialogue, multi_intent_self_instructions = generator.generate_dialogue(entity_name, entity_type, entity_description, sequence_of_intents, conversation_starter)

dialog = solid_generated_dialogue["generated_dialogue"]
print(dialog)
pprint.pprint(dialog, width=80)

```

