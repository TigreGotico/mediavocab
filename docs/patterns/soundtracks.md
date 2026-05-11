# Soundtracks

A soundtrack is a `MUSIC` Work that points at the film / game / drama it
was composed or compiled for. The link is unidirectional from the
soundtrack outward (the film does not carry a "has soundtrack" pointer —
consumers query the relation index by `target.work_hash`).

## Four canonical patterns

1. **Original score** (composed for the work):
   ```python
   score = Work(
       title="Blade Runner (Original Motion Picture Soundtrack)",
       media_type=MediaType.MUSIC, year=1982,
       publication_country="GB",
       relations=[WorkRelation(
           kind=WorkRelationKind.SOUNDTRACK_FOR,
           target=blade_runner,            # the MOVIE Work
       )],
   )
   ```

2. **Compilation soundtrack** (licensed tracks compiled for a film):
   the soundtrack album is a `MUSIC` Work whose `tracklist` Appearances
   are existing music Works. The album→film link is still
   `WorkRelation(SOUNDTRACK_FOR)`:
   ```python
   pulp_fiction_ost = Work(
       title="Pulp Fiction: Music from the Motion Picture",
       media_type=MediaType.MUSIC, year=1994,
       variant_kind=VariantKind.COMPILATION,
       tracklist=[
           Appearance(work=misirlou, position=1),
           Appearance(work=jungle_boogie, position=2),
       ],
       relations=[WorkRelation(kind=WorkRelationKind.SOUNDTRACK_FOR,
                               target=pulp_fiction)],
   )
   ```

3. **Game soundtrack**: same shape as (1) or (2). Target is a `GAME` Work.

4. **Audio drama / audiobook score**: rare — separate score Work with
   `SOUNDTRACK_FOR` pointing at an `AUDIO_DRAMA` or `AUDIOBOOK` Work.

## Why a `WorkRelation`, not a `Credit`?

A `Credit` records *who participated in this Work*. A soundtrack is a
**different Work** that *relates to another Work*. `RelationRole.COMPOSER`
on the composer's credit is set on the score Work (the composer
participated in the score, not in the film itself).
