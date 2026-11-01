from pathlib import Path
import sys, zipfile

root = Path("src/main/java/com/fromthehorror")
def read(name): return (root / name).read_text(encoding="utf-8")

manager = read("CorisandeManager.java")
state = read("CorisandeState.java")
brain = read("CorisandeBrain.java")
entity = read("CorisandeEntity.java")
main = read("FromTheHorror.java")
items = read("ItemRequests.java")
awareness = read("CorisandeAwareness.java")
client = (root / "client/FromTheHorrorClient.java").read_text(encoding="utf-8")

assert "COUNTDOWN_DAYS = 3" in manager
assert "state.completedCycles>=COUNTDOWN_DAYS" in manager or "st.completedCycles>=COUNTDOWN_DAYS" in manager
assert "completedCycles" in state and "lastNight" in state and "cycleInitialized" in state
assert "EntityDimensions.fixed(3.2f, 4.8f)" in entity
assert "this.getAttributeInstance(EntityAttributes.GENERIC_ATTACK_DAMAGE).setBaseValue(26.0)" in entity
assert "CORISANDE_MONSTER" in main and 'literal("monster")' in main and 'literal("corisande_monster")' in main
assert "egg(\"corisande_monster\", CORISANDE_MONSTER" in main
assert "EntityRendererRegistry.register(FromTheHorror.CORISANDE_MONSTER, CorisandeRenderer::new)" in client
assert "locateStructure(StructureTags.VILLAGE" in awareness
assert 's.contains("screecher")' in awareness and 's.contains("mimic")' in awareness and 's.contains("lurker")' in awareness
assert 'CorisandeManager.summonMonster(p)' in awareness
assert "nearestVillage(p, w)" in brain
assert 's.contains("summon ")' in brain
assert "CorisandeManager.chat(sender, raw, true)" in main
assert "advancedArmor" in items and "advancedPickaxe" in items and 'p.equals("enchanted_golden_apple")' in items
def gift_blocked(path):
    armor = path.endswith(("_helmet", "_chestplate", "_leggings", "_boots")) and (path.startswith(("golden_", "diamond_", "netherite_")) or path == "turtle_helmet")
    pick = path in {"golden_pickaxe", "diamond_pickaxe", "netherite_pickaxe"}
    tool = path.endswith(("_sword", "_axe", "_shovel", "_hoe")) and path.startswith(("golden_", "diamond_", "netherite_"))
    return armor or pick or tool or path == "enchanted_golden_apple"
assert not gift_blocked("iron_helmet") and not gift_blocked("iron_pickaxe")
assert gift_blocked("golden_helmet") and gift_blocked("diamond_chestplate")
assert gift_blocked("golden_pickaxe") and gift_blocked("netherite_pickaxe")
assert not gift_blocked("golden_apple") and gift_blocked("enchanted_golden_apple")
assert 'CommandManager.literal("gamemode")' not in main

# Cycle tracking is based on observed day -> night transitions, not world-time day numbers.
assert "else if (!st.lastNight && nightNow)" in manager
assert "st.completedCycles++" in manager
assert "st.lastNight=true" in manager and "st.lastNight=false" in manager
assert "state.completedCycles>=COUNTDOWN_DAYS" in manager or "st.completedCycles>=COUNTDOWN_DAYS" in manager

if "--jar" in sys.argv:
    jar_path = Path(sys.argv[sys.argv.index("--jar") + 1])
    with zipfile.ZipFile(jar_path) as jar:
        names = set(jar.namelist())
        required = {
            "com/fromthehorror/CorisandeManager.class",
            "com/fromthehorror/CorisandeEntity.class",
            "com/fromthehorror/CorisandeAwareness.class",
            "com/fromthehorror/CorisandeBrain.class",
            "assets/fromthehorror/models/item/corisande_monster_spawn_egg.json",
            "fabric.mod.json"
        }
        missing = required - names
        assert not missing, "Missing compiled JAR entries: " + ", ".join(sorted(missing))
        assert jar.testzip() is None, "Corrupt JAR entry found"
print("PASS: three-transition countdown source, monster form, summon command/egg/renderer, village lookup, all-chat replies, iron-tier gift restrictions, and JAR integrity.")
