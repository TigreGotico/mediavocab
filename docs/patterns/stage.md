# Stage productions

`MediaType.STAGE` represents a *production* — a specific staging of a script
or score by a specific director and cast in a specific venue. The script is
a separate Work; the production references it via `WorkRelation.ADAPTED_FROM`.

## Three layers

| Layer | What it is | Model |
|---|---|---|
| Script / score | `Hamlet` (Shakespeare, c.1600) | `Work(media_type=BOOK)` |
| Production | RSC's 2008 Hamlet (Doran/Tennant) | `Work(media_type=STAGE)` |
| Performance | The night of 2008-08-12 at Stratford | `Release(work=production, release_date=…)` |

```python
script = Work(title="Hamlet", media_type=MediaType.BOOK, year=1603,
              credits=[author_credit("William Shakespeare")])

production = Work(
    title="Hamlet",
    media_type=MediaType.STAGE,
    year=2008,
    series_title="Royal Shakespeare Company",
    credits=[
        director_credit("Gregory Doran"),
        Credit(entity=tennant_ref, role="Hamlet", relation_role=RelationRole.ACTOR),
    ],
    external_ids={"theatricalia": "..."},
)

nightly = Release(
    work=production,
    release_date="2008-08-12",
    container="Live",
    extra={"venue": "Royal Shakespeare Theatre, Stratford-upon-Avon"},
)
```

When a production is filmed (NT Live, Met Opera HD), the filmed version is a
separate `MOVIE` Work with `WorkRelation(kind=ADAPTED_FROM, target=production)`.
The `STAGE` Work always represents the live production itself, regardless of
whether any recording exists.

External-ID keys: `ibdb`, `theatricalia`, `operabase`.
