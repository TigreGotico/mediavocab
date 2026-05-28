"""Canonical genre constant spellings. Spec §4.14.

Genre is a free `List[str]` on Work.content_genres. These constants ensure
consistent spelling when the genre is known. Consumers may add their own.

Programme formats (concert, stand-up, talk show, reality, news, sports,
documentary, quiz) live in `mediavocab.taxonomy.programme_format`, not here.
Trailer / behind-the-scenes / reaction / social-clip live in
`mediavocab.taxonomy.content_form`, not here.
"""

# Aesthetic narrative genres
GENRE_HORROR = "horror"
GENRE_COMEDY = "comedy"
GENRE_DRAMA = "drama"
GENRE_THRILLER = "thriller"
GENRE_SCI_FI = "sci_fi"
GENRE_FANTASY = "fantasy"
GENRE_ROMANCE = "romance"
GENRE_WESTERN = "western"
GENRE_MYSTERY = "mystery"
GENRE_ACTION = "action"
GENRE_ADVENTURE = "adventure"
GENRE_CRIME = "crime"
GENRE_WAR = "war"
GENRE_HISTORICAL = "historical"
GENRE_BIOGRAPHY = "biography"
GENRE_MUSICAL = "musical"
GENRE_FAMILY = "family"
GENRE_NOIR = "noir"

# Style / cultural origin
GENRE_ANIMATION = "animation"
GENRE_ANIME = "anime"

# Audio aesthetics
GENRE_RADIO_DRAMA = "radio_drama"
GENRE_ASMR = "asmr"
GENRE_AMBIENT = "ambient"
GENRE_SOUNDSCAPE = "soundscape"
GENRE_NATURE_SOUNDS = "nature_sounds"
GENRE_WHITE_NOISE = "white_noise"

# Sound-effect taxonomy (use with SOUND_EFFECT)
GENRE_SFX_ANIMAL = "sfx_animal"
GENRE_SFX_NATURE = "sfx_nature"
GENRE_SFX_MECHANICAL = "sfx_mechanical"
GENRE_SFX_HUMAN = "sfx_human"
GENRE_SFX_UI = "sfx_ui"
GENRE_SFX_FOLEY = "sfx_foley"

# Comics
GENRE_MANGA = "manga"
GENRE_MANHWA = "manhwa"
GENRE_MANHUA = "manhua"
GENRE_WEBCOMIC = "webcomic"
GENRE_MOTION_COMIC = "motion_comic"

# Written / spoken word
GENRE_POETRY = "poetry"
GENRE_SPOKEN_WORD = "spoken_word"
GENRE_ESSAY = "essay"
GENRE_SHORT_STORY = "short_story"
GENRE_EDUCATIONAL = "educational"

# Photo / image collections
GENRE_PHOTO_BOOK = "photo_book"
GENRE_SLIDESHOW = "slideshow"

# Interactive fiction
GENRE_PARSER_IF = "parser_if"
GENRE_CHOICE_IF = "choice_if"
GENRE_VOICE_GAME = "voice_game"
GENRE_BRANCHING = "branching"

# Music genres (top-level)
GENRE_ROCK = "rock"
GENRE_POP = "pop"
GENRE_JAZZ = "jazz"
GENRE_CLASSICAL = "classical"
GENRE_ELECTRONIC = "electronic"
GENRE_METAL = "metal"
GENRE_PUNK = "punk"
GENRE_FOLK = "folk"
GENRE_BLUES = "blues"
GENRE_COUNTRY = "country"
GENRE_INDIE = "indie"
GENRE_REGGAE = "reggae"
GENRE_LATIN = "latin"
GENRE_HIP_HOP = "hip_hop"
GENRE_RNB = "rnb"
GENRE_SOUL = "soul"
GENRE_FUNK = "funk"
GENRE_DISCO = "disco"

# Music sub-genres (electronic family)
GENRE_HOUSE = "house"
GENRE_TECHNO = "techno"
GENRE_TRANCE = "trance"
GENRE_DUBSTEP = "dubstep"
GENRE_DRUM_AND_BASS = "drum_and_bass"

# Cross-type
GENRE_ADULT = "adult"
GENRE_AI_GENERATED = "ai_generated"

# Television / non-fiction formats (use with EPISODIC_SERIES / TV / PODCAST)
GENRE_VARIETY = "variety"
GENRE_TALK = "talk"
GENRE_COMPILATION = "compilation"
GENRE_INSTRUCTIONAL = "instructional"
GENRE_NATURE = "nature"
GENRE_TRAVEL = "travel"
GENRE_COOKING = "cooking"
GENRE_FITNESS = "fitness"
GENRE_TRUE_CRIME = "true_crime"
GENRE_SELF_HELP = "self_help"

# J-music / anime adjacent
GENRE_VOCALOID = "vocaloid"
GENRE_CITY_POP = "city_pop"

# ---------------------------------------------------------------------------
# Registry — explicit tuple of every canonical genre value.
# Update this when adding new GENRE_* constants above.
# ---------------------------------------------------------------------------

_ALL_GENRES = (
    GENRE_HORROR, GENRE_COMEDY, GENRE_DRAMA, GENRE_THRILLER, GENRE_SCI_FI,
    GENRE_FANTASY, GENRE_ROMANCE, GENRE_WESTERN, GENRE_MYSTERY, GENRE_ACTION,
    GENRE_ADVENTURE, GENRE_CRIME, GENRE_WAR, GENRE_HISTORICAL, GENRE_BIOGRAPHY,
    GENRE_MUSICAL, GENRE_FAMILY, GENRE_NOIR,
    GENRE_ANIMATION, GENRE_ANIME,
    GENRE_RADIO_DRAMA, GENRE_ASMR, GENRE_AMBIENT, GENRE_SOUNDSCAPE,
    GENRE_NATURE_SOUNDS, GENRE_WHITE_NOISE,
    GENRE_SFX_ANIMAL, GENRE_SFX_NATURE, GENRE_SFX_MECHANICAL,
    GENRE_SFX_HUMAN, GENRE_SFX_UI, GENRE_SFX_FOLEY,
    GENRE_MANGA, GENRE_MANHWA, GENRE_MANHUA, GENRE_WEBCOMIC, GENRE_MOTION_COMIC,
    GENRE_POETRY, GENRE_SPOKEN_WORD, GENRE_ESSAY, GENRE_SHORT_STORY, GENRE_EDUCATIONAL,
    GENRE_PHOTO_BOOK, GENRE_SLIDESHOW,
    GENRE_PARSER_IF, GENRE_CHOICE_IF, GENRE_VOICE_GAME, GENRE_BRANCHING,
    GENRE_ROCK, GENRE_POP, GENRE_JAZZ, GENRE_CLASSICAL, GENRE_ELECTRONIC,
    GENRE_METAL, GENRE_PUNK, GENRE_FOLK, GENRE_BLUES, GENRE_COUNTRY,
    GENRE_INDIE, GENRE_REGGAE, GENRE_LATIN, GENRE_HIP_HOP, GENRE_RNB,
    GENRE_SOUL, GENRE_FUNK, GENRE_DISCO,
    GENRE_HOUSE, GENRE_TECHNO, GENRE_TRANCE, GENRE_DUBSTEP, GENRE_DRUM_AND_BASS,
    GENRE_ADULT, GENRE_AI_GENERATED,
    GENRE_VARIETY, GENRE_TALK, GENRE_COMPILATION, GENRE_INSTRUCTIONAL,
    GENRE_NATURE, GENRE_TRAVEL, GENRE_COOKING, GENRE_FITNESS,
    GENRE_TRUE_CRIME, GENRE_SELF_HELP,
    GENRE_VOCALOID, GENRE_CITY_POP,
)

KNOWN_GENRES: frozenset = frozenset(_ALL_GENRES)
