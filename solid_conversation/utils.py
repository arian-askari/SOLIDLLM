# Utility functions like filter_new_turn, trim_to_last_punctuation, etc.

# Intent Instructions

intents_dict = {
    "CQ": {
        "user instruction": "Reply with one question asking for clarification in conversation style.",
        "agent instruction": "Reply with one follow-up response in conversation style.",
        "user generation": "Question:",
        "agent generation": "Response:",
    },
    "FD": {
        "user instruction": "Reply with more details in conversation style.",
        "agent instruction": "Reply with further details in conversation style.",
        "user generation": "Response:",
        "agent generation": "Response:",
    },
    "GG": {
        "user instruction": "Continue the conversation by expressing gratitude for the agent's help.",
        "agent instruction": "Continue the conversation by expressing gratitude for the user's questions.",
        "user generation": "Gratitude:",
        "agent generation": "Gratitude:",
    },
    "PA": {
        "user instruction": "Provide a potential solution or answer in conversation style.",
        "agent instruction": "Provide a potential solution or answer in conversation style.",
        "user generation": "Response:",
        "agent generation": "Response:",
    },
    "IR": {
        "user instruction": "Reply with relevant information.",
        "agent instruction": "Ask the user to provide relevant information needed for their previous question.",
        "user generation": "Response:",
        "agent generation": "Question:",
    },
    "OQ": {
        "user instruction": "Formulate the first question posed by a user that initiates a QA dialogue.",
        "agent instruction": "Formulate an original question posed by an agent.",
        "user generation": "Question:",
        "agent generation": "Question:",
    },
    "FQ": {
        "user instruction": "Formulate a follow-up question from a user, seeking further clarification or information.",
        "agent instruction": "Formulate a follow-up question from an agent, seeking further clarification or information.",
        "user generation": "Question:",
        "agent generation": "Question:",
    },
    "RQ": {
        "user instruction": "Now you are talking from the point of view of a third participant in the conversation. Repeat Question: .",
        "agent instruction": "Now you are talking from the point of view of a third participant in the conversation. Repeat Question: .",
        "user generation": "Third Participant:",
        "agent generation": "Third Participant:",
    },
    "PF": {
        "user instruction": "Express satisfaction and appreciation for a working solution.",
        "agent instruction": "Express satisfaction and appreciation for the conversation.",
        "user generation": "Feedback:",
        "agent generation": "Feedback:",
    },
    "NF": {
        "user instruction": "Convey dissatisfaction for the previous response.",
        "agent instruction": "Convey dissatisfaction for the previous response.",
        "user generation": "Negative Feedback:",
        "agent generation": "Negative Feedback:",
    },
    "JK": {
        "user instruction": "Reply with gibberish information. It can contain emojis.",
        "agent instruction": "Reply with gibberish information. It can contain emojis.",
        "user generation": "Gibberish:",
        "agent generation": "Gibberish:",
    },
    "O": {
        "user instruction": "Reply with a system error. Return N/A",
        "agent instruction": "Reply with a system error. Return N/A",
        "user generation": "System Error:",
        "agent generation": "System Error:",
    },
}


def turn_generation(message, model, tokenizer):
    """Receives a message and prompts the model, it returns the result"""

    tokens = tokenizer(message, return_tensors="pt", truncation=True, padding=True).to(
        0
    )
    outputs = model.generate(
        input_ids=tokens["input_ids"],
        attention_mask=tokens["attention_mask"],
        max_new_tokens=100,
        eos_token_id=tokenizer.eos_token_id,
        pad_token_id=tokenizer.pad_token_id,
    )
    str_output = tokenizer.decode(outputs[0], skip_special_tokens=True)

    return str_output


def filter_new_turn(text, original_message, keyword1, keyword2):
    """Filter new generation by: 1) removing artifacts generated by the LLM (tendency to generate multiple turns)"""

    # Find the start of the new turn
    start_new_turn = text.find(original_message) + len(original_message)
    new_turn = text[start_new_turn:]

    # Check for the presence of both keywords in the new turn
    keyword1_in_new_turn = keyword1 in new_turn
    keyword2_in_new_turn = keyword2 in new_turn

    if (
        keyword1_in_new_turn and keyword2_in_new_turn
    ):  # If both keywords are found, keep the part before the first occurrence of either keyword
        first_keyword_index = min(new_turn.find(keyword1), new_turn.find(keyword2))
        new_turn = new_turn[:first_keyword_index]
    elif (
        keyword1_in_new_turn
    ):  # If only keyword1 is found, keep the part before its occurrence
        new_turn = new_turn[: new_turn.find(keyword1)]
    elif (
        keyword2_in_new_turn
    ):  # If only keyword2 is found, keep the part before its occurrence
        new_turn = new_turn[: new_turn.find(keyword2)]

    return text[:start_new_turn] + new_turn


def trim_to_last_punctuation(text):
    """
    Trims a string to include only the content up to the last punctuation mark ('.', '?', '!').
    After that, it removes empty lines.
    """

    # Finding the last occurrence of punctuation marks
    periods = text.rfind(".")
    questions = text.rfind("?")
    exclamations = text.rfind("!")

    # Identifying the position of the last punctuation mark
    last_punctuation = max(periods, questions, exclamations)

    # Trim the text up to the last punctuation mark
    if last_punctuation != -1:
        text = text[: last_punctuation + 1]

    # Remove all empty lines
    text = "\n".join([line for line in text.split("\n") if line.strip() != ""])

    return text


def get_turn(strings):
    """
    Receives a list of intents and returns the turn in the conversation (either 0 or 1)
    """

    counter = -1

    def update_counter(s):
        nonlocal counter
        counter += not s.startswith("_")
        return counter % 2

    return list(map(update_counter, strings))


def combine_instruction(
    intent, instructions_dict, intents_dict_secondkey, model, tokenizer
):
    content = ""
    for i in intent.split("_"):
        instruction = instructions_dict[i][intents_dict_secondkey]
        content = content + " " + instruction
    content = content.strip()
    combine_prompt = """Provide an instruction based on below content:
  Content: {}
  Instruction: """.format(
        content
    )
    tokens = tokenizer(
        combine_prompt, return_tensors="pt", truncation=True, padding=True
    ).to(0)
    outputs = model.generate(
        input_ids=tokens["input_ids"],
        attention_mask=tokens["attention_mask"],
        max_new_tokens=100,
        eos_token_id=tokenizer.eos_token_id,
        pad_token_id=tokenizer.pad_token_id,
    )
    str_output = tokenizer.decode(outputs[0], skip_special_tokens=True)
    combined_instruction = (
        str_output.split("Instruction: ")[1]
        .replace("\n", " ")
        .replace("\r", " ")
        .strip()
    )
    return combined_instruction


def combine_instructionv2(
    intent, instructions_dict, intents_dict_secondkey, model, tokenizer
):
    content = ""
    middle_inputs = []
    for rank, i in enumerate(intent.split("_")):
        instruction = instructions_dict[i][intents_dict_secondkey]
        content = content + " " + instruction
        middle_inputs.append("Instruction {}: {}\n".format(rank, instruction))
    # print("middle_inputs: ", middle_inputs)
    content = content.strip()
    combine_prompt = """Example1:
Instruction 1: Reply with more details in conversation style.
Instruction 2: Convey dissatisfaction for the previous response.
Merged Instruction: In a conversational style, reply with more details and express dissatisfaction for the previous response.

Example2:
{}
Merged Instruction: """.format(
        "".join(middle_inputs)
    )
    # print("combine_prompt: ", combine_prompt)
    tokens = tokenizer(
        combine_prompt, return_tensors="pt", truncation=True, padding=True
    ).to(0)
    outputs = model.generate(
        input_ids=tokens["input_ids"],
        attention_mask=tokens["attention_mask"],
        max_new_tokens=50,
        eos_token_id=tokenizer.eos_token_id,
        pad_token_id=tokenizer.pad_token_id,
    )
    str_output = tokenizer.decode(outputs[0], skip_special_tokens=True)
    # print(str_output)
    combined_instruction = (
        str_output.split("Example2:")[1]
        .split("Merged Instruction:")[1]
        .strip()
        .split("\n")[0]
    )
    # combined_instruction = str_output.split("Instruction: ")[1].replace("\n", " ").replace("\r", " ").strip()
    return combined_instruction  # combined_instruction
