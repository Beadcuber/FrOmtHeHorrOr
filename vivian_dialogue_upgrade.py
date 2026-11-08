from pathlib import Path

p = Path("src/main/java/com/fromthehorror/CorisandeBrain.java")
s = p.read_text(encoding="utf-8")

old = """    private static boolean any(String s, String... w) {
        for (String x : w) if (s.contains(x)) return true;
        return false;
    }
"""
new = r'''    private static boolean any(String s, String... w) {
        for (String x : w) if (s.contains(x)) return true;
        return false;
    }

    /** Normalize common chat spelling before intent detection (don't/dont, you're/youre, ur, etc.). */
    private static String normalize(String message) {
        String s = message.toLowerCase(Locale.ROOT).replace('\u2019', '\'');
        s = s.replaceAll("\\b(don't|dont)\\b", "do not")
             .replaceAll("\\b(can't|cant)\\b", "cannot")
             .replaceAll("\\b(won't|wont)\\b", "will not")
             .replaceAll("\\b(you're|youre)\\b", "you are")
             .replaceAll("\\b(i'm|im)\\b", "i am")
             .replaceAll("\\b(you've|youve)\\b", "you have")
             .replaceAll("\\b(you'll|youll)\\b", "you will")
             .replaceAll("\\bur\\b", "your")
             .replaceAll("\\bu\\b", "you");
        return s.replaceAll("[^a-z0-9_ ]", " ").replaceAll("\\s+", " ").trim();
    }

    /** Returns 100 for a severe personal attack, 70 for a clear insult, or 0 otherwise. */
    private static int offenseLevel(String s, boolean addressed) {
        // Negated insults and dislike of something else are not attacks on Vivian.
        if (any(s, "i do not hate you", "i do not dislike you", "you are not stupid",
                "you are not dumb", "you are not useless", "i do not want you gone")) return 0;
        boolean directed = addressed || has(s, "you", "your");
        if (!directed) return 0;

        if (any(s, "i hate you", "i really hate you", "i absolutely hate you",
                "i despise you", "i cannot stand you", "i want you gone",
                "i wish you were dead", "you should die", "i will kill you",
                "i am going to kill you", "you are worthless", "you are pathetic",
                "you are disgusting", "you are the worst", "i never want to see you again")) return 100;

        if (any(s, "i do not like you", "i dislike you", "i do not want you here",
                "i am sick of you", "you annoy me", "you are annoying", "you are stupid",
                "you are dumb", "you are an idiot", "you are useless", "you are trash",
                "you suck", "shut up", "go away", "leave me alone", "stop talking",
                "nobody likes you", "you are bad", "you are awful", "you are terrible")) return 70;

        if (has(s, "stupid", "idiot", "dumb", "useless", "worthless", "annoying",
                "trash", "pathetic", "awful", "terrible") && directed) return 60;
        return 0;
    }
'''
if old not in s:
    raise SystemExit("Could not find helper insertion point")
s = s.replace(old, new, 1)

old = """        String s = msg.toLowerCase(Locale.ROOT);
        fallback = false;"""
new = """        String s = normalize(msg);
        fallback = false;"""
if old not in s:
    raise SystemExit("Could not find message normalization point")
s = s.replace(old, new, 1)

old = """        boolean insult = any(s, "stupid", "idiot", "dumb", "shut up", "hate you", "useless", "trash", "kill you", "annoying", "worthless")
                || has(s, "ugly", "die");
        if (insult && (addressed || has(s, "you", "your", "ur"))) {
            String pr = CorisandeManager.bump(p, st, 10, "You pushed me too far.");
            if (pr != null) return pr;
            return st.anger >= 65 ? pick(ANGRY) : pick(HURT);
        }
"""
new = """        int offense = offenseLevel(s, addressed);
        if (offense > 0) {
            String reason = offense >= 100 ? "You told me you hate me. I will remember that." : "You told me you do not want me around.";
            String pr = CorisandeManager.bump(p, st, offense, reason);
            if (pr != null) return pr;
            return st.anger >= 65 ? pick(ANGRY) : pick(HURT);
        }
"""
if old not in s:
    raise SystemExit("Could not find old insult logic")
s = s.replace(old, new, 1)

old = """    private static final String[][] FALLBACK = {
        { "I'm listening. Tell me more.", "Interesting. What else?", "I like it when you talk to me." },
        { "Sometimes I forget what I was about to say.", "Did you notice it's quieter lately?", "Stay close. Closer than that." },
        { "It's coming.", "Do you hear that humming? No? Good.", "I'm so hungry, and you're so warm." }
    };"""
new = """    private static final String[][] FALLBACK = {
        { "I am listening, but I am not sure what you mean. Can you say it another way?", "I caught some of that. What do you mean exactly?", "That is new to me. Tell me what you mean." },
        { "I heard you. I am still deciding what to make of that.", "You are being difficult to understand. Try again.", "I remember what you said. I am thinking about it." },
        { "I heard every word. Choose the next ones carefully.", "Do not mistake my silence for forgetting.", "I understand more than I am telling you." }
    };"""
if old not in s:
    raise SystemExit("Could not find fallback responses")
s = s.replace(old, new, 1)

old = """        if (any(s, "love you", "like you", "best friend", "my friend", "good job", "you're great")) return st.warned ? "Careful what you promise me." : "That makes me really happy. You're my favorite.";"""
new = """        if (any(s, "i love you", "i like you", "i really like you", "best friend", "my friend", "good job", "you are great", "you are awesome", "you are helpful", "you are kind", "you are nice")) return st.warned ? "Careful what you promise me." : "That makes me really happy. You're my favorite.";"""
if old not in s:
    raise SystemExit("Could not find positive-response logic")
s = s.replace(old, new, 1)

p.write_text(s, encoding="utf-8")
print("Updated Vivian dialogue intent and anger handling.")
