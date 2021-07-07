from dateparser import parse
from dateparser.languages import default_loader, Locale
from dateparser.conf import apply_settings
from dateparser.utils import normalize_unicode



@apply_settings
def given_settings(settings=None):

    text = "বৃহষ্পতিবাৰ 1 জুলাই 2009"


    if settings.NORMALIZE:
            text = normalize_unicode(text)

    trst = default_loader.get_locale("as")
    print(trst.translate(text, settings=settings))

given_settings()


