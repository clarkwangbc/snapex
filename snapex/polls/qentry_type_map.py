PAGE_QUESTION_TYPE_MAP = (
	# TextField Input Page held
	("TextField", "TextField"),

	# LikertScale Input Page held
	("7LikertScale", "LikertScale"),
	("5LikertScale", "LikertScale"),
	("LikertScale", "LikertScale"),

	# SimpleText Input Page held
	("SimpleText", "SimpleText"), # A simple Textbox input
    ("MultipleChoice", "SimpleText"), # Select one
    ("MultipleSelect", "SimpleText"), # Select one or more
    ("DateInput", "SimpleText"),
    ("TimeInput", "SimpleText"),
    ("DateTimeInput", "SimpleText"), 

     # Photo Input Page Held
    ("PhotoInput", "PhotoInput"),
    
    # Audio Input Page Held
    ("AudioInput", "AudioInput"),
)

PAGE_TYPES=(
    ("TextField", "Text Field Input Page", 1), # Page contains one textfield for maximum
    ("LikertScale", "Likert-Scale Questions Page", 3), # Page contains 3 likerscale questions for maximum
    ("SimpleText", "Simple Text Input Page", 3), # Support for multiple choices, date/time pickers, simple textbox, etc. 3/page maximum
    ("PhotoInput", "Photo Input Page", 1), # You can take a photo. 1/page
    ("AudioInput", "Audio Input Page", 1), # You can take an audio clip. 1/page
)

def ptype_for_qtype(qtype):
	for tuple in PAGE_QUESTION_TYPE_MAP:
		if tuple[0] == qtype:
			return tuple[1]
	return None

def max_items_for_ptype(ptype):
	for tuple in PAGE_TYPES:
		if tuple[0] == ptype:
			return tuple[2]
	return 0

