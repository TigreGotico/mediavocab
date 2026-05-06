"""Canonical genre constant spellings. Spec §4.9.

Genre is a free `List[str]` on Work.content_genres. These constants ensure
consistent spelling when the genre is known. Consumers may add their own.
"""

# Film and TV
GENRE_DOCUMENTARY = "documentary"
GENRE_ANIMATION = "animation"
GENRE_ANIME = "anime"
GENRE_SHORT_FILM = "short_film"
GENRE_NOIR = "noir"
GENRE_CONCERT = "concert"
GENRE_STAND_UP = "stand_up_comedy"
GENRE_TALK_SHOW = "talk_show"
GENRE_REALITY = "reality"
GENRE_NEWS = "news"
GENRE_SPORTS = "sports"
GENRE_BEHIND_SCENES = "behind_the_scenes"
GENRE_TRAILER = "trailer"

# Audio
GENRE_RADIO_DRAMA = "radio_drama"
GENRE_ASMR = "asmr"
GENRE_AMBIENT = "ambient"
GENRE_SOUNDSCAPE = "soundscape"
GENRE_NATURE_SOUNDS = "nature_sounds"
GENRE_WHITE_NOISE = "white_noise"

# Sound effect taxonomy (use with SOUND_EFFECT)
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

# Written/spoken word
GENRE_POETRY = "poetry"
GENRE_SPOKEN_WORD = "spoken_word"
GENRE_ESSAY = "essay"
GENRE_SHORT_STORY = "short_story"
GENRE_HIP_HOP = "hip_hop"
GENRE_EDUCATIONAL = "educational"

# Photo / image collections (use with BOOK)
GENRE_PHOTO_BOOK = "photo_book"
GENRE_SLIDESHOW = "slideshow"

# Interactive fiction (use with INTERACTIVE_FICTION)
GENRE_PARSER_IF = "parser_if"
GENRE_CHOICE_IF = "choice_if"
GENRE_VOICE_GAME = "voice_game"
GENRE_BRANCHING = "branching"

# Canonical narrative genres (apply to MOVIE / TV / BOOK / COMIC / GAME / IF)
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

# Canonical music genres
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
GENRE_RNB = "rnb"
GENRE_SOUL = "soul"
GENRE_FUNK = "funk"
GENRE_DISCO = "disco"
GENRE_HOUSE = "house"
GENRE_TECHNO = "techno"
GENRE_TRANCE = "trance"
GENRE_DUBSTEP = "dubstep"
GENRE_DRUM_AND_BASS = "drum_and_bass"

# Cross-type
GENRE_ADULT = "adult"
GENRE_AI_GENERATED = "ai_generated"
