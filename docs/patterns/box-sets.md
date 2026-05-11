# Box sets and composite Releases

A box set is a packaging decision (`ReleasePackaging.BOX_SET`), not a
creative work. `Release.contents` aggregates several Works in one Release
without inventing a synthetic container Work.

```python
box = Release(
    work=fellowship,                 # principal headline title
    packaging=ReleasePackaging.BOX_SET,
    edition="Extended Edition Trilogy 4K",
    container="4K UHD Blu-ray",
    contents=[
        Appearance(work=fellowship,  position=1, disc=1),
        Appearance(work=two_towers,  position=2, disc=2),
        Appearance(work=return_king, position=3, disc=3),
    ],
)
```

For a multi-cut single-Work box (theatrical + director's + extended on one
disc), each cut is its own Work (§3.4); the box set lists each cut as an
Appearance in `contents`.

When the box has no headline (a true anthology — three unrelated short films,
a label sampler), create a single Work to act as the headline:

```python
sampler_work = Work(title="Indie Label Sampler 2024",
                    media_type=MediaType.MUSIC, year=2024,
                    variant_kind=VariantKind.COMPILATION)
sampler = Release(work=sampler_work, contents=[...])  # appearances
```

## `Work.tracklist` vs `Release.contents`

| Use case | Where it lives |
|---|---|
| Album tracklist (canonical track order) | `Work.tracklist` |
| DJ mix with `offset`s (single continuous release) | `Work.tracklist` with `Appearance.offset` |
| Box set aggregating *separate* Works | `Release.contents` |
| Anthology Release with no canonical host Work | `Release.contents` + a synthetic anthology Work |
