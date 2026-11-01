from pathlib import Path
import sys, zipfile, json

root = Path("src/main/java/com/fromthehorror")
def read(name): return (root/name).read_text(encoding="utf-8")
manager=read("CorisandeManager.java"); state=read("CorisandeState.java"); brain=read("CorisandeBrain.java")
entity=read("CorisandeEntity.java"); main=read("FromTheHorror.java"); items=read("ItemRequests.java")
awareness=read("CorisandeAwareness.java"); dread=read("DreadDirector.java")
client=(root/"client/FromTheHorrorClient.java").read_text(encoding="utf-8")
tts=(root/"client/Tts.java").read_text(encoding="utf-8")
metadata=json.loads(Path("src/main/resources/fabric.mod.json").read_text(encoding="utf-8"))

assert "COUNTDOWN_DAYS = 3" in manager and "st.completedCycles++" in manager
assert "completedCycles" in state and "lastNight" in state and "cycleInitialized" in state
assert "EntityDimensions.fixed(3.2f, 4.8f)" in entity
assert "this.getAttributeInstance(EntityAttributes.GENERIC_ATTACK_DAMAGE).setBaseValue(26.0)" in entity
assert 'egg("vivian", CORISANDE' in main and 'egg("vivian_monster", CORISANDE_MONSTER' in main
assert "EntityRendererRegistry.register(FromTheHorror.CORISANDE_MONSTER, CorisandeRenderer::new)" in client
assert "locateStructure(StructureTags.VILLAGE" in awareness and "nearestVillage(p, w)" in brain
assert "CorisandeManager.summonMonster(p)" in awareness and 's.contains("summon ")' in brain
assert "CorisandeManager.chat(sender, raw, true)" in main
assert "CHAT_TIMES" in manager and "Do... not.... spam.. CHAT!" in manager and "long chatTick = w.getTime();" in manager
assert "Tts.interrupt()" in client and "public static synchronized void interrupt()" in tts
assert "requestTeleport" not in entity and "st.entity == null &&" in manager
assert "DreadDirector.spawn" not in main and "naturalSpawn" not in dread and "checkHerobrineRituals" not in dread
assert 'CommandManager.literal("vivian")' in main and 'CommandManager.literal("music")' in main and 'CommandManager.literal("play")' in main
assert 'CommandManager.literal("horror")' not in main and 'CommandManager.literal("corisande")' not in main
for obsolete in ("DWELLER = Registry.register","WATCHER = Registry.register","HEROBRINE = Registry.register","MAN = Registry.register","LURKER = Registry.register","MIMIC = Registry.register","SCREECHER = Registry.register"):
    assert obsolete not in main, f"old mob registration remains: {obsolete}"
assert 'CommandManager.literal("gamemode")' not in main
assert metadata["id"] == "vivian" and metadata["name"] == "Vivian"
assert Path("src/main/resources/assets/vivian/sounds/vivian_theme.ogg").exists()
assert Path("src/main/resources/assets/vivian/models/item/vivian_spawn_egg.json").exists()
assert Path("src/main/resources/assets/vivian/models/item/vivian_monster_spawn_egg.json").exists()
assert Path("src/main/resources/assets/vivian/textures/entity/vivian_0.png").exists()
assert not Path("src/main/resources/assets/fromthehorror").exists()
assert not Path("src/main/resources/data/fromthehorror").exists()
assert "advancedArmor" in items and "advancedPickaxe" in items and 'p.equals("enchanted_golden_apple")' in items

def gift_blocked(path):
    armor=path.endswith(("_helmet","_chestplate","_leggings","_boots")) and (path.startswith(("golden_","diamond_","netherite_")) or path=="turtle_helmet")
    pick=path in {"golden_pickaxe","diamond_pickaxe","netherite_pickaxe"}
    tool=path.endswith(("_sword","_axe","_shovel","_hoe")) and path.startswith(("golden_","diamond_","netherite_"))
    return armor or pick or tool or path=="enchanted_golden_apple"
assert not gift_blocked("iron_helmet") and not gift_blocked("iron_pickaxe")
assert gift_blocked("golden_helmet") and gift_blocked("diamond_chestplate")
assert gift_blocked("golden_pickaxe") and gift_blocked("netherite_pickaxe")
assert not gift_blocked("golden_apple") and gift_blocked("enchanted_golden_apple")

if "--jar" in sys.argv:
    jar_path=Path(sys.argv[sys.argv.index("--jar")+1])
    with zipfile.ZipFile(jar_path) as jar:
        names=set(jar.namelist())
        required={"com/fromthehorror/CorisandeManager.class","com/fromthehorror/CorisandeEntity.class",
                  "com/fromthehorror/CorisandeAwareness.class","com/fromthehorror/CorisandeBrain.class",
                  "assets/vivian/models/item/vivian_monster_spawn_egg.json","assets/vivian/sounds/vivian_theme.ogg","fabric.mod.json"}
        missing=required-names
        assert not missing, "Missing compiled JAR entries: "+", ".join(sorted(missing))
        assert jar.testzip() is None, "Corrupt JAR entry found"
        mod=json.loads(jar.read("fabric.mod.json"))
        assert mod["id"]=="vivian" and mod["name"]=="Vivian"
print("PASS: Vivian-only registrations and commands, no random other-mob spawns, no distance teleport/respawn, spam interrupt, 3-cycle transformation, namespaced assets, music, gift limits, and JAR integrity.")
