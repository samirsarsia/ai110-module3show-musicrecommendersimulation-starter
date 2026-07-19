# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

This version is a small content-based recommender: it scores every song in a fixed catalog against a single user's stated preferences and returns the top-k matches with a human-readable explanation for each.

---

## How The System Works

Real-world recommenders (Spotify, YouTube, etc.) mostly work by comparing an item's features against a profile built from a user's past behavior (listens, skips, likes) rather than a profile the user fills out directly, and they often blend content-based signals (song attributes) with collaborative signals (what similar users liked). This simulation focuses only on the content-based half: it assumes explicit user preferences and scores songs directly against them, with no learning from behavior over time.

**`Song` features used:** `genre`, `mood`, `energy`, `tempo_bpm`, `valence`, `danceability`, `acousticness` (loaded from `data/songs.csv`).

**`UserProfile` fields:** `favorite_genre`, `favorite_mood`, `target_energy`, `likes_acoustic`.

**Scoring rule (one song):** each song earns points based on how well it matches the user:
- Exact `genre` match: **+2.0** (weighted highest — genre is the most binding preference)
- Exact `mood` match: **+1.0**
- Energy closeness: **+1.5 × (1 - |song.energy - target_energy|)** — this rewards songs whose energy is *close* to the target rather than simply higher or lower, so a user wanting `energy=0.8` is not automatically pushed toward the highest-energy song in the catalog
- Acoustic bonus: if the user `likes_acoustic`, **+0.5 × song.acousticness**

**Ranking rule (list of songs):** every song in the catalog is scored independently, then the list is sorted by score descending and truncated to the top `k`. The scoring rule answers "how good is this one song for this user," while the ranking rule answers the separate question of "given many scored songs, which ones do we actually show, and in what order" — a system needs both because scoring is a per-item calculation and ranking is a list-level decision.

**Example user profile ("Marcus"):** `{"favorite_genre": "rock", "favorite_mood": "intense", "target_energy": 0.9, "likes_acoustic": False}`. Run against the catalog, this profile's top match is "Storm Runner" (rock, intense, energy 0.91 — score 4.48), and a `{"favorite_genre": "lofi", "favorite_mood": "chill", "target_energy": 0.35}` profile's top match is "Library Rain" (lofi, chill, energy 0.35 — score 4.50) with zero overlap in the top 3 between the two — confirming the profile fields are specific enough to separate "intense rock" from "chill lofi" rather than collapsing toward one generic answer.

### Algorithm Recipe

1. For each song in the catalog, compute a score:
   - `+2.0` if `song.genre == user.favorite_genre`
   - `+1.0` if `song.mood == user.favorite_mood`
   - `+1.5 * (1 - abs(song.energy - user.target_energy))` — always applied, rewards closeness rather than "more energy = better"
   - `+0.5 * song.acousticness` if `user.likes_acoustic` is true
2. Sort all scored songs descending by score.
3. Return the top `k` songs, each paired with a plain-language explanation built from which rules fired.

### Data Flow

```mermaid
flowchart LR
    A[User Prefs<br/>genre, mood, target_energy, likes_acoustic] --> B[Process: Loop over every song in songs.csv]
    B --> C[Score each song<br/>genre +2.0 / mood +1.0 / energy closeness +1.5 / acoustic +0.5]
    C --> D[Sort all scored songs descending]
    D --> E[Output: Top K Recommendations<br/>with explanation]
```

### Expected Biases

- **Genre-dominant weighting**: genre is worth 2x a mood match, so this system will tend to favor "right genre, wrong mood" songs over "right mood, wrong genre" songs — it may under-recommend a great mood match if it's in an unfavored genre.
- **Exact-string matching**: `"pop"` and `"indie pop"` are treated as completely unrelated genres, so users whose stated preference doesn't exactly match the catalog's label get no credit even for a very close genre.
- **Underrepresented catalog corners**: some genres/moods in the expanded catalog (e.g., classical/melancholy, r&b/romantic) have only one song, so any user whose taste centers there has very little to differentiate among — the top recommendation will often be the *only* option rather than the *best* one.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

User profile: genre=pop, mood=happy, energy=0.8

Terminal output from `python -m src.main`:

```
Loaded songs: 18

Top recommendations:

1. Sunrise City — Score: 4.47
   Because: genre match (+2.0); mood match (+1.0); energy 0.82 close to target 0.80 (+1.47)

2. Gym Hero — Score: 3.30
   Because: genre match (+2.0); energy 0.93 close to target 0.80 (+1.30)

3. Rooftop Lights — Score: 2.44
   Because: mood match (+1.0); energy 0.76 close to target 0.80 (+1.44)

4. Night Drive Loop — Score: 1.42
   Because: energy 0.75 close to target 0.80 (+1.42)

5. Riot Anthem — Score: 1.36
   Because: energy 0.89 close to target 0.80 (+1.36)
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Stress Test Profiles

Six profiles run against the current 18-song catalog: three "normal" taste profiles, plus three adversarial/edge cases designed to try to break the scoring logic (a profile with a genre/mood combo that contradicts the requested energy, a profile with no genre/mood at all, and a profile with a genre that doesn't exist in the catalog).

```
=== High-Energy Pop: {'genre': 'pop', 'mood': 'happy', 'energy': 0.9} ===
1. Sunrise City (pop/happy) — Score: 4.38
   Because: genre match (+2.0); mood match (+1.0); energy 0.82 close to target 0.90 (+1.38)
2. Gym Hero (pop/intense) — Score: 3.46
   Because: genre match (+2.0); energy 0.93 close to target 0.90 (+1.46)
3. Rooftop Lights (indie pop/happy) — Score: 2.29
   Because: mood match (+1.0); energy 0.76 close to target 0.90 (+1.29)
4. Storm Runner (rock/intense) — Score: 1.48
   Because: energy 0.91 close to target 0.90 (+1.48)
5. Riot Anthem (punk/aggressive) — Score: 1.48
   Because: energy 0.89 close to target 0.90 (+1.48)

=== Chill Lofi: {'genre': 'lofi', 'mood': 'chill', 'energy': 0.3} ===
1. Library Rain (lofi/chill) — Score: 4.42
   Because: genre match (+2.0); mood match (+1.0); energy 0.35 close to target 0.30 (+1.42)
2. Midnight Coding (lofi/chill) — Score: 4.32
   Because: genre match (+2.0); mood match (+1.0); energy 0.42 close to target 0.30 (+1.32)
3. Focus Flow (lofi/focused) — Score: 3.35
   Because: genre match (+2.0); energy 0.40 close to target 0.30 (+1.35)
4. Spacewalk Thoughts (ambient/chill) — Score: 2.47
   Because: mood match (+1.0); energy 0.28 close to target 0.30 (+1.47)
5. Harvest Moon Road (folk/nostalgic) — Score: 1.50
   Because: energy 0.30 close to target 0.30 (+1.50)

=== Deep Intense Rock: {'genre': 'rock', 'mood': 'intense', 'energy': 0.95} ===
1. Storm Runner (rock/intense) — Score: 4.44
   Because: genre match (+2.0); mood match (+1.0); energy 0.91 close to target 0.95 (+1.44)
2. Gym Hero (pop/intense) — Score: 2.47
   Because: mood match (+1.0); energy 0.93 close to target 0.95 (+1.47)
3. Pulse Overdrive (edm/euphoric) — Score: 1.50
   Because: energy 0.95 close to target 0.95 (+1.50)
4. Iron Verdict (metal/aggressive) — Score: 1.47
   Because: energy 0.97 close to target 0.95 (+1.47)
5. Riot Anthem (punk/aggressive) — Score: 1.41
   Because: energy 0.89 close to target 0.95 (+1.41)

=== ADVERSARIAL — Conflicting prefs (classical/sad genre+mood, but energy target 0.9): {'genre': 'classical', 'mood': 'sad', 'energy': 0.9} ===
1. Nocturne in Blue (classical/melancholy) — Score: 2.45
   Because: genre match (+2.0); energy 0.20 close to target 0.90 (+0.45)
2. Storm Runner (rock/intense) — Score: 1.48
   Because: energy 0.91 close to target 0.90 (+1.48)
3. Riot Anthem (punk/aggressive) — Score: 1.48
   Because: energy 0.89 close to target 0.90 (+1.48)
4. Gym Hero (pop/intense) — Score: 1.46
   Because: energy 0.93 close to target 0.90 (+1.46)
5. Pulse Overdrive (edm/euphoric) — Score: 1.43
   Because: energy 0.95 close to target 0.90 (+1.43)

=== ADVERSARIAL — No genre/mood, just acoustic+low energy: {'energy': 0.1, 'likes_acoustic': True} ===
1. Nocturne in Blue (classical/melancholy) — Score: 1.83
   Because: energy 0.20 close to target 0.10 (+1.35); acousticness 0.95 (+0.47)
2. Spacewalk Thoughts (ambient/chill) — Score: 1.69
   Because: energy 0.28 close to target 0.10 (+1.23); acousticness 0.92 (+0.46)
3. Harvest Moon Road (folk/nostalgic) — Score: 1.61
   Because: energy 0.30 close to target 0.10 (+1.20); acousticness 0.81 (+0.41)
4. Library Rain (lofi/chill) — Score: 1.55
   Because: energy 0.35 close to target 0.10 (+1.12); acousticness 0.86 (+0.43)
5. Coffee Shop Stories (jazz/relaxed) — Score: 1.54
   Because: energy 0.37 close to target 0.10 (+1.09); acousticness 0.89 (+0.45)

=== ADVERSARIAL — Nonexistent genre "reggae" (not in catalog): {'genre': 'reggae', 'mood': 'happy', 'energy': 0.6} ===
1. Rooftop Lights (indie pop/happy) — Score: 2.26
   Because: mood match (+1.0); energy 0.76 close to target 0.60 (+1.26)
2. Sunrise City (pop/happy) — Score: 2.17
   Because: mood match (+1.0); energy 0.82 close to target 0.60 (+1.17)
3. Broken Streetlights (hip-hop/melancholy) — Score: 1.43
   Because: energy 0.55 close to target 0.60 (+1.43)
4. Dust and Diesel (country/nostalgic) — Score: 1.35
   Because: energy 0.50 close to target 0.60 (+1.35)
5. Velvet Whisper (r&b/romantic) — Score: 1.32
   Because: energy 0.48 close to target 0.60 (+1.32)
```

**Key finding — a real bug, not just a quirk:** the "conflicting prefs" adversarial profile exposes a flaw in the scoring model. It asks for `genre=classical, mood=sad, energy=0.9`, and the system's #1 pick, "Nocturne in Blue," matches genre but has an actual energy of 0.20 — a 0.70 gap from the target, the worst energy fit of anything in the top 5. It still wins because a genre match alone (+2.0) outweighs a huge energy mismatch (+0.45). This means the scoring rule has no penalty for a profile that is internally contradictory (a "classical" fan who wants energy 0.9 is asking for something that mostly doesn't exist in this catalog), and no floor/ceiling on how badly a single feature can miss before a match in another feature should stop compensating for it.

Also notable: the "nonexistent genre" profile (`reggae`, not in the catalog) doesn't crash or return nothing — `score_song` just silently skips the genre-match bonus for every song, so the system gracefully degrades to ranking by mood + energy alone. That's safe, but it also means a typo in a genre name (e.g., "pop " with a trailing space) fails exactly the same way as a genuinely absent genre, with no feedback to the user that their preference was never matched.

---

## Experiments You Tried

**Lowering the genre weight from 2.0 to 0.5** (user: `genre=pop, mood=happy, energy=0.8`): with the default weights, "Sunrise City" (pop, happy, energy 0.82) clearly wins with a score of 4.47, well ahead of "Gym Hero" (pop, but wrong mood) at 3.30. Dropping genre's weight to 0.5 shrinks the gap and even lets "Rooftop Lights" (right mood, wrong genre, score 2.44) pass "Gym Hero" (right genre, wrong mood, score 1.80). This confirmed the intuition that genre should dominate mood — with a low genre weight, a mood match started outweighing a genre match, which felt wrong for how people usually describe their taste ("I want something poppy" is a harder constraint than "I want something happy").

**Different user types:**
- A chill/lofi, low-energy user (`genre=lofi, mood=chill, energy=0.3`) correctly surfaced "Library Rain" and "Midnight Coding" at the top — both lofi, chill, and close to the target energy — showing the scoring generalizes past the pop/happy example in [main.py](src/main.py).
- A user with no genre/mood preference who just wants acoustic, low-energy songs (`energy=0.4, likes_acoustic=True`) correctly surfaced "Coffee Shop Stories," "Focus Flow," and "Library Rain" — all high-acousticness, energy-close songs from different genres (jazz, lofi, lofi), showing the acoustic bonus and energy-closeness terms work independently of genre/mood when those preferences aren't specified.

I did not add `tempo_bpm` or `valence` to the score — see Limitations below.

**Weight-shift experiment (`GENRE_WEIGHT` 2.0→1.0, `ENERGY_WEIGHT` 1.5→3.0)**, re-run against the adversarial "conflicting prefs" profile above (`genre=classical, mood=sad, energy=0.9`):

```
BEFORE (GENRE_WEIGHT=2.0, ENERGY_WEIGHT=1.5):
1. Nocturne in Blue — 2.45 — genre match (+2.0); energy 0.20 close to target 0.90 (+0.45)
2. Storm Runner — 1.48 — energy 0.91 close to target 0.90 (+1.48)

AFTER (GENRE_WEIGHT=1.0, ENERGY_WEIGHT=3.0):
1. Storm Runner — 2.97 — energy 0.91 close to target 0.90 (+2.97)
2. Riot Anthem — 2.97 — energy 0.89 close to target 0.90 (+2.97)
3. Gym Hero — 2.91 — energy 0.93 close to target 0.90 (+2.91)
```

With the default weights, a genre match alone was enough to put an energy-mismatched song ("Nocturne in Blue," off by 0.70) in first place. After the shift, "Nocturne in Blue" drops out of the top 5 entirely, replaced by songs whose energy actually matches the target. For this specific profile the change made the recommendations *more* accurate, because the user's numeric preference (`energy: 0.9`) is a much stronger signal of intent than the fact that they happen to like classical music generally. This is a real accuracy improvement for contradictory profiles, but it's also just a different tradeoff, not a strictly better one — for a normal, non-conflicting profile (e.g., High-Energy Pop above), raising `ENERGY_WEIGHT` this much would make near-miss energy songs from the *wrong* genre outrank exact genre matches, which is not obviously an improvement.

---

## Limitations and Risks

- **Tiny catalog**: only 10 songs, so the "best" match for an unusual profile (e.g., high-energy jazz) may still be a weak match — there is nothing better in the data.
- **No listening history or feedback loop**: the system only uses a one-time stated profile (`favorite_genre`, `favorite_mood`, `target_energy`, `likes_acoustic`); it has no way to learn from skips, replays, or thumbs-down the way a real streaming recommender would.
- **Ignores valence, tempo, and danceability**: these are loaded but never scored, so two songs with wildly different tempo or "musical positivity" can tie if their genre, mood, and energy line up. A user who cares specifically about tempo (e.g., for a workout) gets no signal from this system.
- **Exact-match-only for categorical features**: genre and mood must match exactly, so a user who likes "pop" gets zero credit for "indie pop," even though a person would probably call that a close match. This makes the system brittle to how the catalog happens to label things.
- **Fixed weights favor genre by design**: genre gets the highest weight (2.0), so users whose taste is more mood-driven than genre-driven may get recommendations that feel geared toward the wrong axis of their preference.
- **No diversity control**: the top-k list can be dominated by songs from the same artist or genre (e.g., "Sunrise City" and "Night Drive Loop" are both Neon Echo), since the ranking rule sorts purely by score with no artist/genre diversity constraint.

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Building this made concrete something that's easy to gloss over in the abstract: a recommender doesn't "understand" music, it computes a number from whatever features happen to be in the data, and that number is only as good as the features and weights someone chose. The closeness-based scoring for energy (`1 - abs(song.energy - target)`) was the clearest example — a naive "higher energy is better" rule would have completely misrepresented what a user wanting *moderate* energy actually wants, and it's easy to imagine a real system shipping that mistake if nobody stopped to ask what "matching" should mean for a continuous feature.

The bias risk that stood out most is in the weighting and the exact-match logic: giving genre 2x the weight of mood is a design choice that bakes in an assumption about what matters most in "vibe," and it will systematically favor users whose stated genre happens to exist in the catalog under the exact label used — someone who likes "indie pop" but typed "pop" gets penalized for a labeling mismatch, not an actual taste mismatch. At a larger scale, this is the same mechanism behind real-world recommender complaints: whatever gets weighted heavily, or whatever categories the catalog encodes cleanly, ends up structurally favored, regardless of whether that reflects what users actually want.



