# -*- coding: utf-8 -*-
info = {
    "name": "ru",
    "date_order": "DMY",
    "january": [
        "январь",
        "янв",
        "января"
    ],
    "february": [
        "февраль",
        "февр",
        "февраля",
        "Фев"
    ],
    "march": [
        "март",
        "марта",
        "мар"
    ],
    "april": [
        "апрель",
        "апр",
        "апреля"
    ],
    "may": [
        "май",
        "мая"
    ],
    "june": [
        "июнь",
        "июня",
        "июн"
    ],
    "july": [
        "июль",
        "июля",
        "июл"
    ],
    "august": [
        "август",
        "авг",
        "августа"
    ],
    "september": [
        "сентябрь",
        "сент",
        "сентября",
        "Сен"
    ],
    "october": [
        "октябрь",
        "окт",
        "октября"
    ],
    "november": [
        "ноябрь",
        "нояб",
        "ноября",
        "Ноя"
    ],
    "december": [
        "декабрь",
        "дек",
        "декабря"
    ],
    "monday": [
        "понедельник",
        "пн"
    ],
    "tuesday": [
        "вторник",
        "вт"
    ],
    "wednesday": [
        "среда",
        "ср",
        "Среду"
    ],
    "thursday": [
        "четверг",
        "чт"
    ],
    "friday": [
        "пятница",
        "пт",
        "Пятницу"
    ],
    "saturday": [
        "суббота",
        "сб",
        "Субботу"
    ],
    "sunday": [
        "воскресенье",
        "вс",
        "Воскресение",
        "вск"
    ],
    "am": [
        "дп"
    ],
    "pm": [
        "пп"
    ],
    "year": [
        "год",
        "г",
        "года",
        "лет"
    ],
    "month": [
        "месяц",
        "мес",
        "месяца",
        "месяцев"
    ],
    "week": [
        "неделя",
        "нед",
        "недели",
        "недель",
        "неделю"
    ],
    "day": [
        "день",
        "дн",
        "дня",
        "дней"
    ],
    "hour": [
        "час",
        "ч",
        "часа",
        "часов"
    ],
    "minute": [
        "минута",
        "мин",
        "минуты",
        "минут",
        "минуту"
    ],
    "second": [
        "секунда",
        "сек",
        "с",
        "секунды",
        "секунд",
        "секунду"
    ],
    "relative-type": {
        "1 year ago": [
            "в прошлом году"
        ],
        "0 year ago": [
            "в этом году"
        ],
        "in 1 year": [
            "в следующем году"
        ],
        "1 month ago": [
            "в прошлом месяце"
        ],
        "0 month ago": [
            "в этом месяце"
        ],
        "in 1 month": [
            "в следующем месяце"
        ],
        "1 week ago": [
            "на прошлой неделе"
        ],
        "0 week ago": [
            "на этой неделе"
        ],
        "in 1 week": [
            "на следующей неделе"
        ],
        "1 day ago": [
            "вчера"
        ],
        "0 day ago": [
            "сегодня"
        ],
        "in 1 day": [
            "завтра"
        ],
        "0 hour ago": [
            "в этом часе"
        ],
        "0 minute ago": [
            "в эту минуту"
        ],
        "0 second ago": [
            "сейчас"
        ],
        "2 day ago": [
            "позавчера"
        ],
        "in 2 day": [
            "послезавтра"
        ],
        "in 3 day": [
            "послепослезавтра"
        ]
    },
    "relative-type-regex": {
        "in \\1 year": [
            "через (\\d+) год",
            "через (\\d+) года",
            "через (\\d+) г",
            "через (\\d+) лет"
        ],
        "\\1 year ago": [
            "(\\d+) год назад",
            "(\\d+) года назад",
            "(\\d+) г назад",
            "(\\d+) лет назад"
        ],
        "in \\1 month": [
            "через (\\d+) месяц",
            "через (\\d+) месяца",
            "через (\\d+) мес",
            "через (\\d+) месяцев"
        ],
        "\\1 month ago": [
            "(\\d+) месяц назад",
            "(\\d+) месяца назад",
            "(\\d+) мес назад",
            "(\\d+) месяцев назад"
        ],
        "in \\1 week": [
            "через (\\d+) неделю",
            "через (\\d+) недели",
            "через (\\d+) нед",
            "через (\\d+) недель"
        ],
        "\\1 week ago": [
            "(\\d+) неделю назад",
            "(\\d+) недели назад",
            "(\\d+) нед назад",
            "(\\d+) недель назад"
        ],
        "in \\1 day": [
            "через (\\d+) день",
            "через (\\d+) дня",
            "через (\\d+) д",
            "через (\\d+) дн",
            "через (\\d+) дней"
        ],
        "\\1 day ago": [
            "(\\d+) день назад",
            "(\\d+) дня назад",
            "(\\d+) д назад",
            "(\\d+) дн назад",
            "(\\d+) дней назад"
        ],
        "in \\1 hour": [
            "через (\\d+) час",
            "через (\\d+) часа",
            "через (\\d+) ч",
            "через (\\d+) часов"
        ],
        "\\1 hour ago": [
            "(\\d+) час назад",
            "(\\d+) часа назад",
            "(\\d+) ч назад",
            "(\\d+) часов назад"
        ],
        "in \\1 minute": [
            "через (\\d+) минуту",
            "через (\\d+) минуты",
            "через (\\d+) мин",
            "через (\\d+) минут"
        ],
        "\\1 minute ago": [
            "(\\d+) минуту назад",
            "(\\d+) минуты назад",
            "(\\d+) мин назад",
            "(\\d+) минут назад"
        ],
        "in \\1 second": [
            "через (\\d+) секунду",
            "через (\\d+) секунды",
            "через (\\d+) сек",
            "через (\\d+) секунд"
        ],
        "\\1 second ago": [
            "(\\d+) секунду назад",
            "(\\d+) секунды назад",
            "(\\d+) сек назад",
            "(\\d+) секунд назад"
        ]
    },
    "locale_specific": {
        "ru-KZ": {
            "name": "ru-KZ"
        },
        "ru-UA": {
            "name": "ru-UA",
            "am": [
                "am"
            ],
            "pm": [
                "pm"
            ]
        },
        "ru-MD": {
            "name": "ru-MD"
        },
        "ru-KG": {
            "name": "ru-KG"
        },
        "ru-BY": {
            "name": "ru-BY"
        }
    },
    "skip": [
        "около",
        "в",
        "и",
        " ",
        ".",
        ",",
        ";",
        "-",
        "/",
        "'",
        "|",
        "@",
        "[",
        "]",
        "，"
    ],
    "sentence_splitter_group": 1,
    "ago": [
        "назад"
    ],
    "in": [
        "в течение",
        "спустя",
        "через"
    ],
    "simplifications": [
        {
            "час": "1 час"
        },
        {
            "минуту": "1 минуту"
        },
        {
            "секунду": "1 секунду"
        },
        {
            "несколько секунд": "4 секунды"
        }
    ]
}
