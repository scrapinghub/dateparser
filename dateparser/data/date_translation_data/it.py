info = {
    "name": "it",
    "date_order": "DMY",
    "january": [
        "gen",
        "gennaio"
    ],
    "february": [
        "feb",
        "febbraio"
    ],
    "march": [
        "mar",
        "marzo"
    ],
    "april": [
        "apr",
        "aprile"
    ],
    "may": [
        "mag",
        "maggio"
    ],
    "june": [
        "giu",
        "giugno"
    ],
    "july": [
        "lug",
        "luglio"
    ],
    "august": [
        "ago",
        "agosto"
    ],
    "september": [
        "set",
        "settembre"
    ],
    "october": [
        "ott",
        "ottobre"
    ],
    "november": [
        "nov",
        "novembre"
    ],
    "december": [
        "dic",
        "dicembre"
    ],
    "monday": [
        "lun",
        "lunedì"
    ],
    "tuesday": [
        "mar",
        "martedì"
    ],
    "wednesday": [
        "mer",
        "mercoledì"
    ],
    "thursday": [
        "gio",
        "giovedì"
    ],
    "friday": [
        "ven",
        "venerdì"
    ],
    "saturday": [
        "sab",
        "sabato"
    ],
    "sunday": [
        "dom",
        "domenica"
    ],
    "am": [
        "am",
        "mattina"
    ],
    "pm": [
        "pm",
        "pomeriggio"
    ],
    "decade": [
        "decade",
    ],
    "year": [
        "anno",
        "anni"
    ],
    "month": [
        "mese",
        "mesi"
    ],
    "week": [
        "sett",
        "settimana",
        "settimane"
    ],
    "day": [
        "g",
        "giorno",
        "giorni"
    ],
    "hour": [
        "h",
        "ora",
        "ore"
    ],
    "minute": [
        "m",
        "min",
        "minuto",
        "minuti"
    ],
    "second": [
        "s",
        "sec",
        "secondo",
        "secondi"
    ],
    "relative-type": {
        "0 day ago": [
            "oggi"
        ],
        "0 hour ago": [
            "quest'ora"
        ],
        "0 minute ago": [
            "questo minuto"
        ],
        "0 month ago": [
            "questo mese"
        ],
        "0 second ago": [
            "ora"
            "adesso"
        ],
        "0 week ago": [
            "questa settimana"
        ],
        "0 year ago": [
            "quest'anno"
        ],
        "1 day ago": [
            "ieri"
        ],
        "1 month ago": [
            "mese scorso"
        ],
        "1 week ago": [
            "settimana scorsa"
        ],
        "1 year ago": [
            "anno scorso"
        ],
        "in 1 day": [
            "domani"
        ],
        "in 1 month": [
            "mese prossimo"
        ],
        "in 1 week": [
            "settimana prossima"
        ],
        "in 1 year": [
            "anno prossimo"
        ],
        "2 day ago": [
            "altro ieri"
        ]
        "in 2 days": [
            "dopodomani"
        ]
    },
    "relative-type-regex": {
        "\\1 day ago": [
            "(\\d+) g fa",
            "(\\d+) gg fa",
            "(\\d+) giorni fa",
            "(\\d+) giorno fa"
        ],
        "\\1 hour ago": [
            "(\\d+) h fa",
            "(\\d+) ora fa",
            "(\\d+) ore fa"
        ],
        "\\1 minute ago": [
            "(\\d+) min fa",
            "(\\d+) minuti fa",
            "(\\d+) minuto fa"
        ],
        "\\1 month ago": [
            "(\\d+) mese fa",
            "(\\d+) mesi fa"
        ],
        "\\1 second ago": [
            "(\\d+) s fa",
            "(\\d+) sec fa",
            "(\\d+) secondi fa",
            "(\\d+) secondo fa"
        ],
        "\\1 week ago": [
            "(\\d+) sett fa",
            "(\\d+) settimana fa",
            "(\\d+) settimane fa"
        ],
        "\\1 year ago": [
            "(\\d+) anni fa",
            "(\\d+) anno fa"
        ],
        "in \\1 day": [
            "tra (\\d+) g",
            "tra (\\d+) gg",
            "tra (\\d+) giorni",
            "tra (\\d+) giorno"
        ],
        "in \\1 hour": [
            "tra (\\d+) h",
            "tra (\\d+) ora",
            "tra (\\d+) ore"
        ],
        "in \\1 minute": [
            "tra (\\d+) min",
            "tra (\\d+) minuti",
            "tra (\\d+) minuto"
        ],
        "in \\1 month": [
            "tra (\\d+) mese",
            "tra (\\d+) mesi"
        ],
        "in \\1 second": [
            "tra (\\d+) s",
            "tra (\\d+) sec",
            "tra (\\d+) secondi",
            "tra (\\d+) secondo"
        ],
        "in \\1 week": [
            "tra (\\d+) sett",
            "tra (\\d+) settimana",
            "tra (\\d+) settimane"
        ],
        "in \\1 year": [
            "tra (\\d+) anni",
            "tra (\\d+) anno"
        ]
    },
    "locale_specific": {
        "it-CH": {
            "name": "it-CH"
        },
        "it-SM": {
            "name": "it-SM"
        },
        "it-VA": {
            "name": "it-VA"
        }
    },
    "skip": [
        "circa",
        "e",
        "alle",
        "alla",
        "all'",
        "all",
        "a",
        "il",
        "l'", 
        "l", 
        "lo",
        "la",
        "di",
        "del",
        "della",
        "dell'
        " ",
        "'",
        ",",
        "-",
        ".",
        "/",
        ";",
        "@",
        "[",
        "]",
        "|",
        "，"
    ],
    "pertain": [
        "di",
        "del",
        "della",
        "dell'"
    ]
    "sentence_splitter_group": 1,
    "ago": [
        "fa"
        "scorsa"
        "scorso"
    ],
    "in": [
        "in"
        "fra"
        "tra"
        "da ora"
    ],
    "simplifications": [
        {
            "(\\d+)\\s+ora": "\\1 ore"       
        },
        {
            "un[']ora": "1 ore"
        },
        {
            "(?:12\\s+)?mezzogiorno": "12:00"
        },
        {
            "(?:12\\s+)?una": "13:00"
        },
        { 
            "(?:12\\s+)?mezzanotte": "00:00"
        },
        { 
            "(?:12\\s+)?una di notte": "01:00"
        },
        { 
            "(\\d+)h(\\d+)m?": "\\1:\\2"
        },
        { 
            "(?<=from\\s+)now": "tra"
        },
        { 
            "less than 1 minute ago": "pochi secondi fa"
        },
        { 
            "un": "1"
        },    
        { 
            "due": "2"
        },
        { 
            "tre": "3"
        },
        { 
            "quattro": "4"
        },  
        { 
            "cinque": "5"
        },   
        { 
            "sei": "6"
        },  
        { 
            "sette": "7"
        },   
        { 
            "otto": "8"
        },  
        { 
            "nove": "9"
        },  
        { 
            "dieci": "10"
        },   
        { 
            "undici": "11"
        },  
        { 
            "dodici": "12"
        },    
    ]
}
