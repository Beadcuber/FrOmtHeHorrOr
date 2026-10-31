from pathlib import Path
import sys

root = Path(sys.argv[1]) / "src/main/java/com/fromthehorror"

def replace(path, old, new, count=1):
    p = root / path
    s = p.read_text(encoding="utf-8")
    if old not in s:
        raise SystemExit(f"Patch target not found in {path}: {old[:100]!r}")
    s = s.replace(old, new, count)
    p.write_text(s, encoding="utf-8")

# Five in-game days between Corisande's warning and her transformation.
replace("CorisandeManager.java", "public static final int REALLY_MAD = 70;", "public static final int REALLY_MAD = 100;\n    public static final int COUNTDOWN_DAYS = 5;")
replace("CorisandeManager.java", "st.madDay + 14 - day", "st.madDay + COUNTDOWN_DAYS - day")
replace("CorisandeManager.java", "st.madDay + 14)", "st.madDay + COUNTDOWN_DAYS)")
replace("CorisandeManager.java", ' : 14;', ' : COUNTDOWN_DAYS;')
replace("CorisandeManager.java", '"Something is coming in 14 days, "', '"Something is coming in " + COUNTDOWN_DAYS + " days, "')
replace("CorisandeManager.java", 'told the player something is coming in 14 days.', 'told the player something is coming in 5 days.')
replace("CorisandeManager.java", 'bump(p, st, 30, "You shouldn\\'t have hit me.")', 'bump(p, st, 12, "You shouldn\\'t have hit me.")')
replace("CorisandeManager.java", '"Fourteen days. I told you something was coming."', '"Five days. I told you something was coming."')
replace("CorisandeManager.java", "if (st.anger >= 55) return 3;", "if (st.anger >= 75) return 3;")
replace("CorisandeManager.java", "if (st.anger >= 35) return 2;", "if (st.anger >= 50) return 2;")
replace("CorisandeManager.java", "if (st.anger >= 15) return 1;", "if (st.anger >= 25) return 1;")
replace("CorisandeManager.java", "st.anger >= 35 ? 1 : 0", "st.anger >= 50 ? 1 : 0")
replace("CorisandeManager.java", "else if (st.anger >= 35) mood =", "else if (st.anger >= 50) mood =")

# Corisande takes longer to become angry: fewer points per insult/hit and more patience around gifts.
replace("CorisandeBrain.java", '"Fourteen days, and now it\\'s time."', '"Five days, and now it\\'s time."')
replace("CorisandeBrain.java", "st.madDay + 14 - day", "st.madDay + CorisandeManager.COUNTDOWN_DAYS - day")
replace("CorisandeBrain.java", " : 14;", " : CorisandeManager.COUNTDOWN_DAYS;")
replace("CorisandeBrain.java", "st.anger >= 35 ? 1 : 0", "st.anger >= 50 ? 1 : 0")
replace("CorisandeBrain.java", 'bump(p, st, 25, "You pushed me too far.")', 'bump(p, st, 10, "You pushed me too far.")')
replace("CorisandeBrain.java", "st.anger >= 45 ? pick(ANGRY) : pick(HURT)", "st.anger >= 65 ? pick(ANGRY) : pick(HURT)")
replace("CorisandeBrain.java", "if (st.anger >= 55) return", "if (st.anger >= 75) return")
replace("CorisandeBrain.java", "st.greed += cost;", "st.greed += cost * 0.5;")
replace("CorisandeBrain.java", "if (st.greed >= HARD_LIMIT) {", "if (st.greed >= HARD_LIMIT * 1.5) {")
replace("CorisandeBrain.java", "if (st.greed >= SOFT_LIMIT) {\n            st.anger = Math.min(69, st.anger + 20);", "if (st.greed >= SOFT_LIMIT * 1.25) {\n            st.anger = Math.min(99, st.anger + 10);")

# Add a separate natural-encounter timer so the monsters appear in the world, not only from scare rolls.
replace("DreadDirector.java", "private static final Map<UUID, Integer> TIMERS = new HashMap<>();",
"""private static final Map<UUID, Integer> TIMERS = new HashMap<>();
    private static final Map<UUID, Integer> NATURAL_SPAWN_TIMERS = new HashMap<>();""")
replace("DreadDirector.java", """            int t = TIMERS.getOrDefault(p.getUuid(), nextDelay()) - 1;
            if (t > 0) { TIMERS.put(p.getUuid(), t); continue; }
            TIMERS.put(p.getUuid(), nextDelay());
            trigger(world, p);""",
"""            int t = TIMERS.getOrDefault(p.getUuid(), nextDelay()) - 1;
            if (t > 0) {
                TIMERS.put(p.getUuid(), t);
            } else {
                TIMERS.put(p.getUuid(), nextDelay());
                trigger(world, p);
            }

            // A natural monster encounter attempt roughly every 2-4 minutes per player.
            int natural = NATURAL_SPAWN_TIMERS.getOrDefault(p.getUuid(), 2200 + R.nextInt(2600)) - 1;
            if (natural > 0) {
                NATURAL_SPAWN_TIMERS.put(p.getUuid(), natural);
            } else {
                NATURAL_SPAWN_TIMERS.put(p.getUuid(), 2200 + R.nextInt(2600));
                naturalSpawn(world, p);
            }""")
replace("DreadDirector.java", "    private static void fog(ServerWorld w, ServerPlayerEntity p) {",
"""    /** Natural world encounters: Dweller in caves, Watcher/Herobrine and the Man at night or in storms. */
    private static void naturalSpawn(ServerWorld w, ServerPlayerEntity p) {
        BlockPos pos = p.getBlockPos();
        boolean underground = !w.isSkyVisible(pos) && pos.getY() < 56;
        boolean nightOrStorm = w.isNight() || w.isRaining();
        int roll = R.nextInt(100);

        if (underground) {
            if (roll < 65) spawn(w, p, FromTheHorror.DWELLER, 24, 38);
            else if (roll < 80 && nightOrStorm) spawn(w, p, FromTheHorror.MAN, 30, 44);
        } else if (nightOrStorm) {
            if (roll < 45) spawn(w, p, FromTheHorror.WATCHER, 30, 46);
            else if (roll < 85) spawn(w, p, FromTheHorror.MAN, 28, 42);
        } else if (roll < 8) {
            spawn(w, p, FromTheHorror.MAN, 32, 48);
        }
        // Corisande is already automatically spawned and maintained by CorisandeManager.tick().
    }

    private static void fog(ServerWorld w, ServerPlayerEntity p) {""")

# Give players easy custom-command aliases as well as the vanilla /summon IDs.
replace("FromTheHorror.java", """                    .then(CommandManager.literal("watcher").executes(c -> {
                        DreadDirector.spawn(c.getSource().getWorld(), c.getSource().getPlayerOrThrow(), WATCHER, 20, 26); return 1; }))""",
"""                    .then(CommandManager.literal("watcher").executes(c -> {
                        DreadDirector.spawn(c.getSource().getWorld(), c.getSource().getPlayerOrThrow(), WATCHER, 20, 26); return 1; }))
                    .then(CommandManager.literal("herobrine").executes(c -> {
                        DreadDirector.spawn(c.getSource().getWorld(), c.getSource().getPlayerOrThrow(), WATCHER, 20, 26); return 1; }))
                    .then(CommandManager.literal("corisande").executes(c -> {
                        CorisandeManager.summon(c.getSource().getPlayerOrThrow()); return 1; }))""")

print("Applied five-day countdown, slower anger, natural monster encounters, and summon aliases.")
