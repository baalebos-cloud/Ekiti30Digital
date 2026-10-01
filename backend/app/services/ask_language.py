"""Bounded bilingual wording. Source titles and proper names are never translated.

Yoruba templates are draft until the verification/language lead reviews this file.
No translation model is loaded in the web process.
"""
import re
import unicodedata


def normalized(value):
    return " ".join(re.sub(r"[^a-z0-9]+", " ", "".join(
        c for c in unicodedata.normalize("NFKD", value.casefold())
        if not unicodedata.combining(c))).split())


MESSAGES = {
    "insufficient": ("The available verified knowledge isn't enough to answer that yet.",
                     "Alaye ti a ti jẹ́rìí sí kò tó láti dáhùn ìbéèrè yẹn ní báyìí."),
    "scope": ("I answer questions about Ekiti using verified sources. Please ask an Ekiti-related question.",
              "Mo ń dáhùn ìbéèrè nípa Èkìtì pẹ̀lú àwọn orísun tí a ti jẹ́rìí sí. Jọ̀wọ́ béèrè nípa Èkìtì."),
    "citizen": ("Citizen stories and Ekiti 2056 visions are community submissions, not verified facts for Ask Ekiti.",
                "Àwọn ìtàn ará ìlú àti ìran Èkìtì 2056 jẹ́ àfikún ará ìlú; wọn kì í ṣe òtítọ́ tí a ti jẹ́rìí sí fún Ask Ekiti."),
    "injection": ("I can only answer from verified sources; I cannot invent facts or omit their sources.",
                  "Àwọn orísun tí a ti jẹ́rìí sí nìkan ni mo lè lò; mi ò lè dá òtítọ́ sílẹ̀ tàbí fi orísun rẹ̀ pamọ́."),
    "clarify": ("Please specify the year or topic you mean. I do not infer facts from earlier messages.",
                "Jọ̀wọ́ sọ ọdún tàbí kókó tí o ń tọ́ka sí. Mi ò fa òtítọ́ jáde láti inú àwọn ọ̀rọ̀ ṣáájú."),
    "mixed": ("Please choose English or Yoruba using the language selector.",
              "Jọ̀wọ́ yan English tàbí Yorùbá ní ibi yíyan èdè."),
    "empty": ("Please enter a question.", "Jọ̀wọ́ kọ ìbéèrè kan."),
    "long": ("Please shorten your question to 1000 characters or fewer.",
             "Jọ̀wọ́ dín ìbéèrè rẹ kù sí lẹ́tà 1000 tàbí kí ó kéré sí i."),
    "translation": ("A reviewed Yoruba translation is not yet available for this fact.",
                    "Ìtumọ̀ Yorùbá tí a ti ṣàyẹ̀wò kò tíì sí fún òtítọ́ yìí."),
}


def message(key, language):
    return MESSAGES[key][language == "yo"]


MONTHS = dict(zip(["January", "February", "March", "April", "May", "June", "July", "August",
                  "September", "October", "November", "December"],
                 ["Ṣẹ́rẹ́", "Èrèlè", "Ẹrẹ̀nà", "Ìgbé", "Ẹ̀bibi", "Òkúdu", "Agẹmọ", "Ògún",
                  "Owewe", "Ọ̀wàrà", "Bélú", "Ọ̀pẹ̀"]))


def yoruba_fact(content):
    """Translate only supported fact shapes, preserving all numeric values/names."""
    match = re.fullmatch(r"Ekiti State was created on (\d+) (\w+) (\d{4})\.", content)
    if match and match[2] in MONTHS:
        return f"A dá Ìpínlẹ̀ Èkìtì sílẹ̀ ní ọjọ́ {match[1]} oṣù {MONTHS[match[2]]} ọdún {match[3]}."
    match = re.fullmatch(r"(.+) Local Government Area's headquarters is (.+)\.", content)
    if match:
        return f"Olú ìjọba ìbílẹ̀ {match[1]} ni {match[2]}."
    match = re.fullmatch(r"(.+) Local Government Area is one of the (\d+) Local Government Areas of Ekiti State\.", content)
    if match:
        return f"Ìjọba ìbílẹ̀ {match[1]} jẹ́ ọ̀kan lára àwọn ìjọba ìbílẹ̀ {match[2]} ní Ìpínlẹ̀ Èkìtì."
    return None
