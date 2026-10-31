from pathlib import Path
p=Path("finish_mobs.py")
s=p.read_text(encoding="utf-8")
a=s.index("# Natural encounters:")
b=s.index("# Texture variants",a)
patch = """# Natural encounters: replace the full method; mod_patch.py already changed its old body.
director = java / "DreadDirector.java"
src = director.read_text(encoding="utf-8")
start = src.index("    private static void naturalSpawn")
end = src.index("    private static void fog", start)
method = \"\"\"    private static void naturalSpawn(ServerWorld w, ServerPlayerEntity p) {
        BlockPos pos = p.getBlockPos();
        boolean underground = !w.isSkyVisible(pos) && pos.getY() < 56;
        boolean nightOrStorm = w.isNight() || w.isRaining();
        int roll = R.nextInt(100);
        if (underground) {
            if (roll < 42) spawn(w, p, FromTheHorror.DWELLER, 24, 38);
            else if (roll < 62) spawn(w, p, FromTheHorror.LURKER, 22, 36);
            else if (roll < 76) spawn(w, p, FromTheHorror.MIMIC, 22, 38);
            else if (roll < 88 && nightOrStorm) spawn(w, p, FromTheHorror.MAN, 30, 44);
        } else if (nightOrStorm) {
            if (roll < 22) spawn(w, p, FromTheHorror.SCREECHER, 28, 44);
            else if (roll < 45) spawn(w, p, FromTheHorror.MIMIC, 28, 44);
            else if (roll < 68) spawn(w, p, FromTheHorror.WATCHER, 30, 46);
            else if (roll < 85) spawn(w, p, FromTheHorror.MAN, 28, 42);
        } else if (roll < 8) {
            spawn(w, p, FromTheHorror.MAN, 32, 48);
        }
    }

    \"\"\"
director.write_text(src[:start] + method + src[end:], encoding="utf-8")

"""
p.write_text(s[:a]+patch+s[b:],encoding="utf-8")
print("Updated the monster patch to replace the current natural-spawn method safely.")
