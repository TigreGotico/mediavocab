# Soundtracks

See spec §8.5. Four canonical patterns:

1. **Original score** (composed for the work): score Work has
   `WorkRelation(kind=SOUNDTRACK_FOR, target=film_work)`. Score's
   `media_type=MediaType.MUSIC`.
2. **Compilation soundtrack** (licensed tracks compiled for the film):
   the soundtrack album is a `Work` (`MUSIC`) whose `tracklist` Appearances
   are existing music Works. The album→film link is `SOUNDTRACK_FOR`.
3. **Game soundtrack**: same as 1 or 2; `WorkRelation` target has
   `media_type=MediaType.GAME`.
4. **Audio drama / audiobook score**: rare — a separate score Work with
   `SOUNDTRACK_FOR` linking to the audio drama Work.

The film/game itself does not need a "has soundtrack" link — the relation
is unidirectional from the soundtrack Work outward.
