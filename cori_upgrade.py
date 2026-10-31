from pathlib import Path
import json

root = Path("src/main/java/com/fromthehorror")

def edit(rel, old, new, count=1):
    p = root / rel
    s = p.read_text(encoding="utf-8")
    if old not in s:
        raise SystemExit("Patch target missing in " + rel + ": " + old[:120])
    p.write_text(s.replace(old, new, count), encoding="utf-8")

# The fifth cycle completes at the end of its night, never at dawn.
edit("CorisandeManager.java",
     "if (st.warned && !st.turned && day >= st.madDay + COUNTDOWN_DAYS) turnNow(w);",
     "if (st.warned && !st.turned && day >= st.madDay + COUNTDOWN_DAYS && w.isNight()) turnNow(w);")

# Make the large form genuinely monstrous.
# The special monster egg creates an independent hostile Corisande, not the world's bonded orb.
edit("CorisandeEntity.java",
     "this.setCustomNameVisible(true);\n    }",
     "this.setCustomNameVisible(true);\n        if (type == FromTheHorror.CORISANDE_MONSTER) turn();\n    }")
edit("CorisandeEntity.java",
     "if (st.entity != null && !st.entity.equals(this.getUuid()) && this.age > 40) { this.discard(); return; }",
     "if (getType() == FromTheHorror.CORISANDE && st.entity != null && !st.entity.equals(this.getUuid()) && this.age > 40) { this.discard(); return; }")
edit("CorisandeEntity.java",
     "            CorisandeState st = CorisandeState.get(sw);\n            st.dead = true;",
     "            if (getType() == FromTheHorror.CORISANDE_MONSTER) return;\n            CorisandeState st = CorisandeState.get(sw);\n            st.dead = true;")

# New monster entity type, spawn egg, and dedicated commands.
p = root / "FromTheHorror.java"
s = p.read_text(encoding="utf-8")
s = s.replace("    public static EntityType<CorisandeEntity> CORISANDE;\n",
"""    public static EntityType<CorisandeEntity> CORISANDE;
    public static EntityType<CorisandeEntity> CORISANDE_MONSTER;
""", 1)
s = s.replace("""        FabricDefaultAttributeRegistry.register(CORISANDE, CorisandeEntity.createAttributes());
""", """        CORISANDE_MONSTER = Registry.register(Registries.ENTITY_TYPE, new Identifier(ID, "corisande_monster"),
                FabricEntityTypeBuilder.create(SpawnGroup.MONSTER, CorisandeEntity::new)
                        .dimensions(EntityDimensions.fixed(3.2f, 4.8f)).trackRangeBlocks(128).build());
        FabricDefaultAttributeRegistry.register(CORISANDE, CorisandeEntity.createAttributes());
        FabricDefaultAttributeRegistry.register(CORISANDE_MONSTER, CorisandeEntity.createAttributes());
""", 1)
s = s.replace("""        Item e4 = egg("corisande", CORISANDE, 0xff9628, 0x7a1010);
""", """        Item e4 = egg("corisande", CORISANDE, 0xff9628, 0x7a1010);
        Item e8 = egg("corisande_monster", CORISANDE_MONSTER, 0x120b12, 0x9b111f);
""", 1)
s = s.replace("e.add(e1); e.add(e2); e.add(e3); e.add(e4); e.add(e5); e.add(e6); e.add(e7);",
              "e.add(e1); e.add(e2); e.add(e3); e.add(e4); e.add(e5); e.add(e6); e.add(e7); e.add(e8);", 1)
s = s.replace("""                .then(CommandManager.literal("summon").executes(c -> {
                    CorisandeManager.summon(c.getSource().getPlayerOrThrow()); return 1; }))
""", """                .then(CommandManager.literal("summon").executes(c -> {
                    CorisandeManager.summon(c.getSource().getPlayerOrThrow()); return 1; }))
                .then(CommandManager.literal("monster").executes(c -> {
                    CorisandeManager.summonMonster(c.getSource().getPlayerOrThrow()); return 1; }))
""", 1)
s = s.replace("""                    .then(CommandManager.literal("corisande").executes(c -> {
                        CorisandeManager.summon(c.getSource().getPlayerOrThrow()); return 1; }))
""", """                    .then(CommandManager.literal("corisande").executes(c -> {
                        CorisandeManager.summon(c.getSource().getPlayerOrThrow()); return 1; }))
                    .then(CommandManager.literal("corisande_monster").executes(c -> {
                        CorisandeManager.summonMonster(c.getSource().getPlayerOrThrow()); return 1; }))
""", 1)
# countdown status should explain that zero means she is waiting for night.
s = s.replace('"Exactly " + remaining + " Minecraft days remain until Corisande transforms."',
              'remaining == 0 ? "The fifth cycle is complete. Corisande will transform when night falls." : "Exactly " + remaining + " full Minecraft day/night cycles remain until Corisande transforms."')
p.write_text(s, encoding="utf-8")

# Monster-form summon helper.
p = root / "CorisandeManager.java"
s = p.read_text(encoding="utf-8")
anchor = """    public static void turnNow(ServerWorld w) {
"""
helper = """    public static void summonMonster(ServerPlayerEntity p) {
        ServerWorld w = p.getServerWorld();
        BlockPos pos = DreadDirector.findSpot(w, p, 8, 14);
        if (pos == null) pos = p.getBlockPos().up();
        CorisandeEntity monster = FromTheHorror.CORISANDE_MONSTER.create(w);
        if (monster == null) return;
        monster.refreshPositionAndAngles(pos.getX() + 0.5, pos.getY(), pos.getZ() + 0.5, p.getYaw(), 0);
        monster.turn();
        w.spawnEntity(monster);
        say(p, "You wanted to see what I look like without the disguise. Now run.", true);
        w.playSound(null, pos, SoundEvents.ENTITY_WITHER_SPAWN, SoundCategory.HOSTILE, 1.0f, 0.42f);
    }

"""
if anchor not in s: raise SystemExit("Missing turnNow insertion point")
s = s.replace(anchor, helper + anchor, 1)
p.write_text(s, encoding="utf-8")

# Limit gifts to iron-tier equipment. Golden apples remain allowed; enchanted golden apples do not.
p = root / "ItemRequests.java"
s = p.read_text(encoding="utf-8")
old = """    private static boolean banned(String p) {
        return p.contains("command_block")"""
new = """    private static boolean banned(String p) {
        boolean advancedArmor = (p.endsWith("_helmet") || p.endsWith("_chestplate") || p.endsWith("_leggings") || p.endsWith("_boots"))
                && (p.startsWith("golden_") || p.startsWith("diamond_") || p.startsWith("netherite_") || p.equals("turtle_helmet"));
        boolean advancedPickaxe = p.equals("golden_pickaxe") || p.equals("diamond_pickaxe") || p.equals("netherite_pickaxe");
        boolean advancedCombatTool = (p.endsWith("_sword") || p.endsWith("_axe") || p.endsWith("_shovel") || p.endsWith("_hoe"))
                && (p.startsWith("golden_") || p.startsWith("diamond_") || p.startsWith("netherite_"));
        return advancedArmor || advancedPickaxe || advancedCombatTool || p.equals("enchanted_golden_apple")
                || p.contains("command_block")"""
if old not in s: raise SystemExit("Missing ItemRequests banned()")
s = s.replace(old, new, 1)
p.write_text(s, encoding="utf-8")

# Corisande can locate the nearest village in loaded/server structure data and report coordinates.
p = root / "CorisandeAwareness.java"
s = p.read_text(encoding="utf-8")
s = s.replace("import net.minecraft.registry.Registries;", "import net.minecraft.registry.Registries;\nimport net.minecraft.registry.tag.StructureTags;", 1)
anchor = """    public static String registryLookup(String query) {
"""
village = """    public static String nearestVillage(ServerPlayerEntity p, ServerWorld w) {
        BlockPos origin = p.getBlockPos();
        BlockPos village = w.locateStructure(StructureTags.VILLAGE, origin, 128, false);
        if (village == null) return "I searched for a village nearby, but none was found within my search range. We may need to travel farther.";
        int dx = village.getX() - origin.getX();
        int dz = village.getZ() - origin.getZ();
        int distance = (int) Math.sqrt((double) dx * dx + (double) dz * dz);
        String[] directions = {"east","south-east","south","south-west","west","north-west","north","north-east"};
        int dir = (int)Math.round(Math.atan2(dz, dx) / (Math.PI / 4.0));
        dir = (dir % 8 + 8) % 8;
        return "I found the nearest village I can locate. It is about " + distance + " blocks " + directions[dir]
                + ", near X " + village.getX() + ", Z " + village.getZ() + ". Stay close. Villages attract things at night.";
    }

"""
if anchor not in s: raise SystemExit("Missing registryLookup insertion point")
s = s.replace(anchor, village + anchor, 1)
p.write_text(s, encoding="utf-8")

# Ensure ordinary chat is heard too, not just messages prefixed with her name.
p = root / "FromTheHorror.java"
s = p.read_text(encoding="utf-8")
s = s.replace("sender.getServer().execute(() -> CorisandeManager.chat(sender, raw, addressed));",
              "sender.getServer().execute(() -> CorisandeManager.chat(sender, raw, true));", 1)
p.write_text(s, encoding="utf-8")

# Improve conversational answers, including nearest-village awareness and countdown-at-night nuance.
p = root / "CorisandeBrain.java"
s = p.read_text(encoding="utf-8")
s = s.replace('''            return left == 0 ? "Zero days. It is time." : "Exactly " + left + (left == 1 ? " Minecraft day remains" : " Minecraft days remain") + " until I transform. You can keep count. I already have.";''',
'''            return left == 0 ? (w.isNight() ? "Zero days. It is time. Look at me." : "The fifth cycle is complete. I am waiting for nightfall.") : "Exactly " + left + (left == 1 ? " full day/night cycle remains" : " full day/night cycles remain") + " until I transform. You can keep count. I already have.";''', 1)
s = s.replace('''        if (any(s, "what is happening", "what's happening", "describe this place", "analyze the world", "what do you see", "look around")) return CorisandeAwareness.worldReport(p, w);''',
'''        if (any(s, "nearest village", "closest village", "where is the village", "find a village", "locate a village", "village near")) return CorisandeAwareness.nearestVillage(p, w);
        if (any(s, "what is happening", "what's happening", "describe this place", "analyze the world", "what do you see", "look around")) return CorisandeAwareness.worldReport(p, w);''', 1)
s = s.replace("You can only claim knowledge supported by these live facts. You can summon hostile mobs only when the player explicitly asks.",
              "You can only claim knowledge supported by these live facts. You can summon hostile mobs only when the player explicitly asks. Never run, suggest executing, or claim to execute Minecraft commands. Never change gamemode, permissions, or operator status. Be emotionally expressive, remember conversational context, and answer the player's actual question.", 1)
p.write_text(s, encoding="utf-8")

# Spawn-egg item model and localized name.
resources = Path("src/main/resources/assets/fromthehorror")
models = resources / "models/item"
models.mkdir(parents=True, exist_ok=True)
(models / "corisande_monster_spawn_egg.json").write_text('{ "parent": "minecraft:item/template_spawn_egg" }\n', encoding="utf-8")
lang = resources / "lang/en_us.json"
data = json.loads(lang.read_text(encoding="utf-8"))
data["item.fromthehorror.corisande_monster_spawn_egg"] = "Corisande Monster Spawn Egg"
data["entity.fromthehorror.corisande_monster"] = "Corisande (Monster)"
lang.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

# Register a renderer for the separate monster entity type as well.
p = root / "client/FromTheHorrorClient.java"
s = p.read_text(encoding="utf-8")
old = "        EntityRendererRegistry.register(FromTheHorror.CORISANDE, CorisandeRenderer::new);"
if old not in s: raise SystemExit("Missing Corisande renderer registration")
s = s.replace(old, old + "\n        EntityRendererRegistry.register(FromTheHorror.CORISANDE_MONSTER, CorisandeRenderer::new);", 1)
p.write_text(s, encoding="utf-8")

print("Applied night-gated five-cycle transformation, village location, chat responses, monster summon/egg, and iron-tier gift limits.")
