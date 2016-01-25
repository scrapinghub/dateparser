.. _language-data-template:

Language Data Template
----------------------

.. sourcecode:: none

	two-letter language code as defined in ISO-639-1 (https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes). e.g. for English - en:
	    name: language name (e.g. English)
	    no_word_spacing: False (set to True for languages that do not use spaces between words)
	
	    skip: ["words", "to", "skip", "such", "as", "and", "or", "at"]
	
	    pertain: []
	
	    monday:
	        - name for Monday
	        - abbreviation for Monday
	    tuesday:
	        - as above
	    wednesday:
	        - as above
	    thursday:
	        - as above
	    friday:
	        - as above
	    saturday:
	        - as above
	    sunday:
	        - as above
	
	    january:
	        - name for January
	        - abbreviation for January
	    february:
	        - as above
	    march:
	        - as above
	    april:
	        - as above
	    may:
	        - as above
	    june:
	        - as above
	    july:
	        - as above
	    august:
	        - as above
	    september:
	        - as above
	    october:
	        - as above
	    november:
	        - as above
	    december:
	        - as above
	
	    year:
	        - name for year
	        - abbreviation for year
	    month:
	        - as above
	    week:
	        - as above
	    day:
	        - as above
	    hour:
	        - as above
	    minute:
	        - as above
	    second:
	        - as above
	
	    ago:
	        - words that stand
	        - for "ago"
	
	    simplifications:
	        - word: replacement
	        - regex: replacement
	        - day before yesterday: 2 days ago
