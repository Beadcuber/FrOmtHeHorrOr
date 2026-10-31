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
# The hosted runner does not include Pillow; reuse the mod's bundled textures.
f=Path("finish_mobs.py")
t=f.read_text(encoding="utf-8")
a=t.index("# Texture variants")
b=t.index("lang =",a)
texture_patch = """# Reuse the bundled entity textures; the new mobs have their own model layers and scales.
tex = project / "src/main/resources/assets/fromthehorror/textures/entity"
for src,dst in [("dweller.png","lurker.png"),("watcher.png","mimic.png"),("man_from_the_fog.png","screecher.png"),
                ("dweller_eyes.png","lurker_eyes.png"),("watcher_eyes.png","mimic_eyes.png"),("man_from_the_fog_eyes.png","screecher_eyes.png")]:
    shutil.copyfile(tex/src,tex/dst)

"""
f.write_text(t[:a]+texture_patch+t[b:],encoding="utf-8")
# Spawn egg models need explicit item-model parents on Minecraft 1.20.1.
f=Path("finish_mobs.py")
t=f.read_text(encoding="utf-8")
anchor='print("Registered and rendered The Lurker, The Mimic, and The Screecher; added spawn eggs, commands, textures, and natural encounters.")'
extra="""models = project / "src/main/resources/assets/fromthehorror/models/item"
models.mkdir(parents=True, exist_ok=True)
for mob in ("lurker", "mimic", "screecher"):
    (models / (mob + "_spawn_egg.json")).write_text('{ "parent": "minecraft:item/template_spawn_egg" }\\n', encoding="utf-8")
"""
if anchor not in t: raise SystemExit("Missing finish script completion marker")
f.write_text(t.replace(anchor,extra+anchor,1),encoding="utf-8")
print("Updated natural spawning and removed the Pillow dependency from texture setup.")
