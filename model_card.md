# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

**VibeMatch 1.0**

---

## 2. Intended Use  

This is a classroom simulation, not a real product. It's designed to show, in the simplest possible way, how a "content-based" recommender turns a user's stated taste into a ranked list of songs.

It assumes the user can describe their taste directly — a favorite genre, a favorite mood, a target energy level, and whether they like acoustic songs. Real streaming apps rarely ask for this directly; they infer it from listening history instead. This system skips that inference step entirely and just takes the preferences as given.

It is not intended for real users, real catalogs, or any decision that matters. It's a teaching tool for understanding scoring and ranking logic, built on a tiny, hand-made 18-song catalog.

---

## 3. How the Model Works  

Every song gets a score built from four simple rules:

- If the song's genre matches the user's favorite genre, it gets a solid bonus.
- If the song's mood matches the user's favorite mood, it gets a smaller bonus.
- The closer the song's energy is to the user's target energy, the more points it earns — a song that's too calm or too intense compared to what the user asked for loses points, even if it's a genre match.
- If the user says they like acoustic songs, more acoustic songs get an extra boost.

Genre counts for the most (twice as much as mood), because a genre preference feels like a harder rule ("I want pop") while mood feels more like a mild suggestion ("I want happy"). Once every song has a score, the system just sorts the whole list from highest to lowest and shows the top few, along with a plain-language reason for each one (e.g., "genre match (+2.0)").

The starter file had no logic at all — every function was a placeholder. What was actually built: exact genre/mood matching, closeness-based energy scoring (instead of "higher is always better"), an optional acoustic bonus, and a sorted top-k ranking with explanations attached.

---

## 4. Data  

The catalog has 18 songs total: the original 10 from the starter file plus 8 added later to broaden genre/mood coverage.

Genres represented: pop, indie pop, lofi, rock, ambient, jazz, synthwave, hip-hop, folk, metal, r&b, classical, EDM, country, and punk. Moods: happy, chill, intense, relaxed, moody, focused, melancholy, nostalgic, aggressive, romantic, and euphoric.

Several genres and moods have only one song representing them (classical, r&b, country, EDM), so a user whose taste centers there has almost nothing to differentiate among — whatever song exists in that genre becomes the top pick almost by default, not because it's actually a great match. The dataset also has no lyrics, artist popularity, release year, or cultural/regional signal — it only captures a narrow, numeric slice of "vibe."

---

## 5. Strengths  

The system works best for users whose taste is internally consistent — where genre, mood, and energy all point the same direction. The three ordinary stress-test profiles (High-Energy Pop, Chill Lofi, Deep Intense Rock) all got top picks that felt obviously right: "Sunrise City" for pop/happy/high-energy, "Library Rain" for lofi/chill/low-energy, "Storm Runner" for rock/intense/high-energy. In each case the #1 result matched genre, mood, and energy all at once, which is exactly the kind of match a person would nod along to.

The energy-closeness rule is the piece I'm most confident actually captures something real about "vibe": rewarding *closeness* rather than "higher is always better" means a user who wants moderate energy (say, 0.5) doesn't get pushed toward the most intense song in the catalog just because intensity scores well on some other axis. That felt like the right call the moment I saw it work — a naive "more energy = more points" rule would have been obviously wrong for anyone who doesn't want maximum intensity.

The acoustic-only test (no genre/mood, just `energy=0.1, likes_acoustic=True`) also worked the way I'd expect: it surfaced quiet, acoustic songs from completely different genres (classical, ambient, folk, lofi, jazz), showing the numeric features can carry a recommendation on their own when a user doesn't state a genre/mood preference at all.

---

## 6. Limitations and Bias 

The clearest bug showed up when testing a deliberately contradictory profile: `genre=classical, mood=sad, energy=0.9`. The top result, "Nocturne in Blue," matched the genre but had an actual energy of 0.20 — 0.70 away from what the user asked for, the worst energy fit of anything in the top 5. It still won because a genre match alone (+2.0 points) is worth more than even a terrible energy mismatch (+0.45 points in that case). In other words, the scoring rule has no limit on how much a single categorical match can compensate for a wildly wrong numerical feature, so a system can confidently recommend something that doesn't actually fit what the user described, as long as one field lines up.

A second bias: genre is weighted twice as heavily as mood, so the system will always favor "right genre, wrong mood" songs over "right mood, wrong genre" songs. That's a deliberate design choice, but it also means users whose taste is more mood-driven than genre-driven (e.g., someone who cares more about "feeling chill" than "must be lofi specifically") get recommendations that lean toward the wrong axis of their actual preference.

The dataset itself is also a bias source: genres with only one song (classical, r&b, country, EDM) get recommended almost by default to any user who mentions them, not because that song is a strong match — it's just the only option.

---

## 7. Evaluation  

Six profiles were tested against the 18-song catalog: three ordinary tastes (High-Energy Pop, Chill Lofi, Deep Intense Rock) and three adversarial ones designed to try to break the scoring — a profile with contradictory genre/mood vs. energy (classical/sad but energy 0.9), a profile with no genre or mood at all (just low energy + likes acoustic), and a profile requesting a genre that doesn't exist in the catalog (reggae).

The three ordinary profiles all worked as expected — each one's top pick was an exact genre+mood+energy match, and the top 5 stayed thematically consistent (e.g., Chill Lofi's list was all low-energy, chill-coded songs). The "nonexistent genre" profile didn't crash or behave oddly — it degraded gracefully to ranking by mood and energy alone, which is a reasonable fallback.

The genuinely surprising result was the "conflicting prefs" profile, described in Limitations above — an energy-mismatched song still won on genre alone. A follow-up experiment doubled `ENERGY_WEIGHT` (1.5 → 3.0) and halved `GENRE_WEIGHT` (2.0 → 1.0) and re-ran that same profile: the energy-mismatched song dropped out of the top 5 entirely, replaced by songs whose energy actually matched. That fixed the specific bug, but it's a tradeoff, not a pure improvement — with energy weighted that heavily, a normal profile like High-Energy Pop would start letting energy-close songs from the *wrong* genre outrank exact genre matches, which isn't obviously better either.

Full terminal output for all six profiles and the weight-shift experiment is in the README's [Stress Test Profiles](README.md#stress-test-profiles) and [Experiments You Tried](README.md#experiments-you-tried) sections.

---

## 8. Future Work  

1. **Cap how much one feature can compensate for another.** The "conflicting prefs" bug (a genre match propping up a song with a wildly wrong energy) happened because there's no ceiling on cross-feature compensation. A better version would treat a huge energy mismatch as a near-disqualifier, not just a small deduction, regardless of how well other fields match.
2. **Fuzzy genre/mood matching.** Right now "pop" and "indie pop" are unrelated to the scorer. A similarity table (or even just substring matching) would stop the system from penalizing users for using a slightly different label than the catalog does.
3. **Learn weights from feedback instead of hardcoding them.** `GENRE_WEIGHT`, `MOOD_WEIGHT`, etc. are fixed numbers I chose based on intuition. A more realistic system would adjust these per-user based on skips/replays, the way real recommenders use listening history instead of a one-time stated profile.

(I already implemented one improvement — a diversity penalty that stops the top-k from being dominated by one artist's back catalog — during the stretch-challenge round; see `ARTIST_REPEAT_PENALTY` in `src/recommender.py`.)

---

## 9. Personal Reflection  

The biggest learning moment was seeing the "conflicting prefs" adversarial test actually break the system — I expected the scoring rules to behave reasonably by construction, but running `genre=classical, mood=sad, energy=0.9` and watching "Nocturne in Blue" (energy 0.20, nowhere close to 0.9) win purely on a genre match made it concrete that a scoring rule can be individually sensible (each term looks fine on its own) while the *combination* still produces a bad recommendation. That's a small-scale version of a real ML failure mode: a model can pass every unit-level sanity check and still fail on inputs nobody explicitly designed for.

Using an AI assistant sped up the mechanical parts a lot — writing the CSV loader, wiring up the scoring math, running six stress-test profiles and a weight-shift experiment in seconds instead of by hand. The place I had to double-check it most was exactly the compensation behavior above: it's easy for an assistant (or a person) to implement each scoring rule correctly in isolation and never notice that they interact badly until you deliberately try to break them with an adversarial profile.

What surprised me most is how "smart" a handful of `if` statements and one weighted-distance formula can feel. There's no learning, no lyrics, no listening history — just genre/mood equality checks and `1 - abs(energy - target)` — and yet the top results for a clear profile like "chill lofi, low energy" felt genuinely right. It reframed how I think about real recommendation apps: a lot of what feels like "the algorithm understands me" might just be a few well-chosen, well-weighted rules applied to good features, not some deep understanding of taste.

If I extended this further, I'd want to try the weight-learning idea from Future Work — instead of picking `GENRE_WEIGHT = 2.0` because it felt right, actually simulate a user giving feedback (thumbs up/down) and adjust the weights based on that, to see how much the "right" weights differ from my initial guesses.
