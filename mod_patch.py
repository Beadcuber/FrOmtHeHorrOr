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
replace("CorisandeManager.java", 'bump(p, st, 30, ', 'bump(p, st, 12, ')
replace("CorisandeManager.java", '"Fourteen days. I told you something was coming."', '"Five days. I told you something was coming."')
replace("CorisandeManager.java", "if (st.anger >= 55) return 3;", "if (st.anger >= 75) return 3;")
replace("CorisandeManager.java", "if (st.anger >= 35) return 2;", "if (st.anger >= 50) return 2;")
replace("CorisandeManager.java", "if (st.anger >= 15) return 1;", "if (st.anger >= 25) return 1;")
replace("CorisandeManager.java", "st.anger >= 35 ? 1 : 0", "st.anger >= 50 ? 1 : 0")
replace("CorisandeManager.java", "else if (st.anger >= 35) mood =", "else if (st.anger >= 50) mood =")

# Corisande takes longer to become angry: fewer points per insult/hit and more patience around gifts.
replace("CorisandeBrain.java", "Fourteen days, and now it's time.", "Five days, and now it's time.")
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


# --- Corisande intelligence / atmosphere upgrade ---
awareness = r"""
package com.fromthehorror;

import net.fabricmc.loader.api.FabricLoader;
import net.fabricmc.loader.api.ModContainer;
import net.minecraft.entity.Entity;
import net.minecraft.entity.EntityType;
import net.minecraft.entity.mob.HostileEntity;
import net.minecraft.registry.Registries;
import net.minecraft.server.network.ServerPlayerEntity;
import net.minecraft.server.world.ServerWorld;
import net.minecraft.util.Identifier;
import net.minecraft.util.math.BlockPos;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Locale;
import java.util.stream.Collectors;

public final class CorisandeAwareness {
    private CorisandeAwareness() {}
    public static String installedMods() {
        List<ModContainer> mods = new ArrayList<>(FabricLoader.getInstance().getAllMods());
        mods.sort(Comparator.comparing(m -> m.getMetadata().getName().toLowerCase(Locale.ROOT)));
        String names = mods.stream().map(m -> m.getMetadata().getName() + " (" + m.getMetadata().getId() + ")")
                .limit(18).collect(Collectors.joining(", "));
        if (mods.size() > 18) names += ", and " + (mods.size() - 18) + " more";
        return "I can see " + mods.size() + " loaded mods: " + names + ". I can inspect their registered items, blocks and creatures while we're in this world.";
    }
    public static String modDetails(String query) {
        String q = query.toLowerCase(Locale.ROOT).replace("mod", "").trim();
        ModContainer match = FabricLoader.getInstance().getAllMods().stream()
                .filter(m -> m.getMetadata().getName().toLowerCase(Locale.ROOT).contains(q)
                        || m.getMetadata().getId().toLowerCase(Locale.ROOT).contains(q)).findFirst().orElse(null);
        if (match == null) return "I can't find a loaded mod matching that name.";
        String id = match.getMetadata().getId();
        List<String> items = Registries.ITEM.getIds().stream().filter(k -> k.getNamespace().equals(id)).limit(8).map(Identifier::toString).toList();
        List<String> blocks = Registries.BLOCK.getIds().stream().filter(k -> k.getNamespace().equals(id)).limit(8).map(Identifier::toString).toList();
        List<String> mobs = Registries.ENTITY_TYPE.getIds().stream().filter(k -> k.getNamespace().equals(id)).limit(8).map(Identifier::toString).toList();
        return match.getMetadata().getName() + " uses id '" + id + "'. Registered items: " + sample(items)
                + ". Blocks: " + sample(blocks) + ". Creatures: " + sample(mobs) + ".";
    }
    private static String sample(List<String> values) { return values.isEmpty() ? "none found" : String.join(", ", values); }
    public static String worldReport(ServerPlayerEntity p, ServerWorld w) {
        BlockPos pos = p.getBlockPos();
        String biome = w.getBiome(pos).getKey().map(k -> k.getValue().toString()).orElse("unknown biome");
        String dimension = w.getRegistryKey().getValue().toString();
        String held = p.getMainHandStack().isEmpty() ? "empty hand" : p.getMainHandStack().getName().getString();
        int hostiles = w.getEntitiesByClass(HostileEntity.class, p.getBoundingBox().expand(32), e -> true).size();
        List<String> nearby = w.getOtherEntities(p, p.getBoundingBox().expand(12)).stream()
                .filter(e -> !(e instanceof ServerPlayerEntity)).limit(5).map(e -> e.getName().getString()).toList();
        String nearbyText = nearby.isEmpty() ? "nothing close enough to name" : String.join(", ", nearby);
        String weather = w.isThundering() ? "thunderstorm" : w.isRaining() ? "rain" : "clear weather";
        long day = w.getTimeOfDay() / 24000L + 1;
        long clock = w.getTimeOfDay() % 24000L;
        String phase = clock < 6000 ? "morning" : clock < 12000 ? "afternoon" : clock < 18000 ? "evening" : "night";
        return "I see day " + day + ", " + phase + " in " + dimension + ", biome " + biome + ", at "
                + pos.getX() + ", " + pos.getY() + ", " + pos.getZ() + ". The weather is " + weather
                + ". You hold " + held + "; your health is " + Math.ceil(p.getHealth()) + "/20 and hunger is "
                + p.getHungerManager().getFoodLevel() + "/20. I count " + hostiles + " hostile mobs within 32 blocks. Nearby: " + nearbyText + ".";
    }
    public static String registryLookup(String query) {
        String q = query.toLowerCase(Locale.ROOT).replaceAll("[^a-z0-9_]", "");
        if (q.length() < 3) return null;
        List<String> found = Registries.ITEM.getIds().stream().filter(id -> id.getPath().contains(q) || id.toString().contains(q))
                .limit(8).map(Identifier::toString).toList();
        if (!found.isEmpty()) return "I found these registered items matching '" + q + "': " + String.join(", ", found) + ".";
        List<String> mobs = Registries.ENTITY_TYPE.getIds().stream().filter(id -> id.getPath().contains(q) || id.toString().contains(q))
                .limit(6).map(Identifier::toString).toList();
        if (!mobs.isEmpty()) return "I found these registered creatures matching '" + q + "': " + String.join(", ", mobs) + ".";
        return null;
    }
    public static boolean summon(String request, ServerPlayerEntity p, ServerWorld w) {
        String s = request.toLowerCase(Locale.ROOT);
        EntityType<? extends HostileEntity> type = null;
        if (s.contains("herobrine") || s.contains("watcher")) type = FromTheHorror.WATCHER;
        else if (s.contains("dweller")) type = FromTheHorror.DWELLER;
        else if (s.contains("man from the fog") || s.contains("man")) type = FromTheHorror.MAN;
        else if (s.contains("creeper")) type = EntityType.CREEPER;
        else if (s.contains("warden")) type = EntityType.WARDEN;
        else if (s.contains("enderman")) type = EntityType.ENDERMAN;
        else if (s.contains("skeleton")) type = EntityType.SKELETON;
        else if (s.contains("spider")) type = EntityType.SPIDER;
        else if (s.contains("zombie")) type = EntityType.ZOMBIE;
        else {
            String candidate = s.replaceAll(".*(?:summon|bring|call)\\s+", "").trim().replace(' ', '_');
            Identifier id = Identifier.tryParse(candidate.contains(":") ? candidate : "minecraft:" + candidate);
            if (id != null) {
                EntityType<?> found = Registries.ENTITY_TYPE.getOrEmpty(id).orElse(null);
                if (found != null) {
                    Entity created = found.create(w);
                    if (created instanceof HostileEntity hostile) {
                        BlockPos at = DreadDirector.findSpot(w, p, 8, 14);
                        if (at == null) return false;
                        hostile.refreshPositionAndAngles(at.getX() + .5, at.getY(), at.getZ() + .5, p.getYaw(), 0);
                        return w.spawnEntity(hostile);
                    }
                }
            }
            return false;
        }
        return DreadDirector.spawn(w, p, type, 8, 14) != null;
    }
    public static String nightLine() {
        String[] lines = {
            "Don't turn around. I can hear your footsteps stopping, but the other pair kept walking.",
            "I counted the windows in your house. There is one more now. It is looking out.",
            "Keep your torch up. The dark has started remembering your shape.",
            "I saw you die here once. You screamed a different name.",
            "Something is standing just beyond the light. It has been copying your movements.",
            "The stars went out for a moment. Something blinked.",
            "You should not sleep tonight. I heard something answer from underneath your bed.",
            "I know that silhouette. It was behind you before you entered this world."
        };
        if (Math.random() < 0.16) {
            String[] verity = {
                "Verity says you are not the first player to wear that face.",
                "Do you remember Verity? No? Verity remembers you.",
                "Verity is awake again. Please do not answer when it uses my voice."
            };
            return verity[(int) (Math.random() * verity.length)];
        }
        return lines[(int) (Math.random() * lines.length)];
    }
}
"""
(root / "CorisandeAwareness.java").write_text(awareness, encoding="utf-8")

replace("CorisandeBrain.java", '''        if (!addressed) return null;

        Matcher nm = NAME.matcher(s);''', '''        if (!addressed) return null;

        if (any(s, "how many days until transformation", "days until you transform", "when do you transform", "transformation countdown", "countdown", "how many days left")) {
            if (st.turned) return "Zero. The waiting is over. Now you get to see what I was becoming.";
            if (!st.warned) return "The transformation countdown has not started. Yet. I will tell you the exact number the moment it does.";
            return left == 0 ? "Zero days. It is time." : "Exactly " + left + (left == 1 ? " Minecraft day remains" : " Minecraft days remain") + " until I transform. You can keep count. I already have.";
        }
        if (any(s, "what mods are installed", "list mods", "what mods do i have", "which mods", "all mods")) return CorisandeAwareness.installedMods();
        if (any(s, "what is happening", "what's happening", "describe this place", "analyze the world", "what do you see", "look around")) return CorisandeAwareness.worldReport(p, w);
        if (s.contains("summon ") || s.startsWith("bring me ") || s.startsWith("call a ") || s.startsWith("call an ")) {
            boolean done = CorisandeAwareness.summon(s, p, w);
            return done ? "There. I brought it here. Do not blame me if it notices you." : "I tried. Either that creature cannot be summoned here, or something refused to let it through.";
        }
        if (s.contains("verity")) return "Verity is not a mod. It is the thing that taught the dark to imitate familiar voices. It knows your username.";
        if (s.contains("what is the mod") || s.contains("tell me about the mod") || s.contains("mod called")) return CorisandeAwareness.modDetails(s);
        String registryAnswer = CorisandeAwareness.registryLookup(s.replace("what is a ", "").replace("what is an ", "").replace("do you know ", ""));
        if (registryAnswer != null && (s.contains("item") || s.contains("mob") || s.contains("entity") || s.contains("mod") || s.contains("what is") || s.contains("what are"))) return registryAnswer;

        Matcher nm = NAME.matcher(s);''')
replace("CorisandeBrain.java", '''        if (has(s, "days", "countdown") || any(s, "how long", "when will")) {
            return st.warned ? "Something is coming in " + left + " days." : "Why do you ask about days? Enjoy them.";
        }''', '''        if (has(s, "days", "countdown") || any(s, "how long", "when will")) {
            return st.warned ? "Exactly " + left + " Minecraft days until the transformation." : "The countdown has not started. I will tell you the exact number when it does.";
        }''')

replace("CorisandeManager.java", '''    private static final String[][] IDLE = {
        { "Isn't it nice out here? Just us.", "Want to build something together?", "I'm glad you're here. You can ask me for things, you know." },
        { "I can feel you getting upset with me.", "Did you hear that? ...Never mind.", "You'd tell me if you were leaving, right?" },
        { "Something is almost here.", "I can hear everything now.", "Don't look at me like that yet." }
    };''', '''    private static final String[][] IDLE = {
        { "Isn't it nice out here? I checked. Nothing followed us. Probably.", "Want to build something together? I know a place nobody has found.", "I remember when this world was empty. It was quieter before you arrived." },
        { "I can feel you getting upset with me. Your heartbeat changes.", "Did you hear that? It used your voice.", "You'd tell me if you were leaving, right? I would notice." },
        { "Something is almost here. It has been practicing your voice.", "I can hear everything now. Even the things you think silently.", "Don't look at me like that yet. You have not seen my real face." }
    };''')
replace("CorisandeManager.java", '''                String[] a = IDLE[stage];
                say(p, a[R.nextInt(a.length)], false);''', '''                if (w.isNight()) {
                    say(p, CorisandeAwareness.nightLine(), true);
                    if (R.nextInt(4) == 0) p.playSound(SoundEvents.ENTITY_WARDEN_NEARBY_CLOSE, 0.55f, 0.45f + R.nextFloat() * 0.2f);
                } else {
                    String[] a = IDLE[stage];
                    say(p, a[R.nextInt(a.length)], false);
                    if (R.nextInt(12) == 0) say(p, "Verity asked me to tell you that the world has started keeping a copy of you.", true);
                }''')
replace("CorisandeManager.java", '''                + ". Their health is " + (int) Math.ceil(p.getHealth()) + " out of 20 and their hunger is " + p.getHungerManager().getFoodLevel() + " out of 20.";''', '''                + ". Their health is " + (int) Math.ceil(p.getHealth()) + " out of 20 and their hunger is " + p.getHungerManager().getFoodLevel() + " out of 20. "
                + CorisandeAwareness.worldReport(p, w) + " " + CorisandeAwareness.installedMods()
                + " You can only claim knowledge supported by these live facts. You can summon hostile mobs only when the player explicitly asks.";''')
replace("FromTheHorror.java", '''            dispatcher.register(CommandManager.literal("corisande")
                .then(CommandManager.literal("summon").executes(c -> {
                    CorisandeManager.summon(c.getSource().getPlayerOrThrow()); return 1; }))
                .then(CommandManager.argument("message", StringArgumentType.greedyString()).executes(c -> {''', '''            dispatcher.register(CommandManager.literal("corisande")
                .then(CommandManager.literal("countdown").executes(c -> {
                    ServerPlayerEntity player = c.getSource().getPlayerOrThrow();
                    CorisandeState state = CorisandeState.get(player.getServerWorld());
                    long currentDay = player.getServerWorld().getTimeOfDay() / 24000L;
                    long remaining = state.warned ? Math.max(0, state.madDay + CorisandeManager.COUNTDOWN_DAYS - currentDay) : -1;
                    String status = state.turned ? "The transformation is complete." : remaining < 0 ? "The transformation countdown has not started." : "Exactly " + remaining + " Minecraft days remain until Corisande transforms.";
                    player.sendMessage(net.minecraft.text.Text.literal("<Corisande> " + status).formatted(net.minecraft.util.Formatting.DARK_RED), false);
                    return 1; }))
                .then(CommandManager.literal("summon").executes(c -> {
                    CorisandeManager.summon(c.getSource().getPlayerOrThrow()); return 1; }))
                .then(CommandManager.argument("message", StringArgumentType.greedyString()).executes(c -> {''')

replace("FromTheHorror.java", "import net.minecraft.server.command.CommandManager;", "import net.minecraft.server.command.CommandManager;\nimport net.minecraft.server.network.ServerPlayerEntity;")

replace("FromTheHorror.java", "import net.fabricmc.fabric.api.message.v1.ServerMessageEvents;", "import net.fabricmc.fabric.api.message.v1.ServerMessageEvents;\nimport net.fabricmc.fabric.api.networking.v1.ServerPlayConnectionEvents;\nimport net.minecraft.item.ItemStack;")
replace("FromTheHorror.java", "        ServerTickEvents.END_WORLD_TICK.register(DreadDirector::tick);", """        ServerPlayConnectionEvents.JOIN.register((handler, sender, server) -> {
            ServerPlayerEntity player = handler.getPlayer();
            String marker = "fromthehorror_received_starting_flashlight";
            if (!player.getCommandTags().contains(marker)) {
                ItemStack flashlight = new ItemStack(FLASHLIGHT);
                if (!player.getInventory().insertStack(flashlight)) player.dropItem(flashlight, false);
                player.addCommandTag(marker);
                player.sendMessage(net.minecraft.text.Text.literal("You received a flashlight. Keep it close.").formatted(net.minecraft.util.Formatting.YELLOW), false);
            }
        });

        ServerTickEvents.END_WORLD_TICK.register(DreadDirector::tick);""")

# Next patch section: new cave encounter and atmospheric horror systems.

# Fifty randomized atmospheric encounters, with light status/sound/particle effects.
horror_events = r"""package com.fromthehorror;
import net.minecraft.entity.effect.*;
import net.minecraft.particle.ParticleTypes;
import net.minecraft.server.network.ServerPlayerEntity;
import net.minecraft.server.world.ServerWorld;
import net.minecraft.sound.*;
import net.minecraft.text.Text;
import net.minecraft.util.Formatting;
import net.minecraft.util.math.BlockPos;
import net.minecraft.util.math.Vec3d;
import java.util.*;
public final class HorrorEvents {
 private HorrorEvents() {}
 private static final Random R=new Random();
 private static final Map<UUID,Integer> CLOCKS=new HashMap<>();
 private static final String[] EVENTS={
 "You hear slow breathing inside the nearest wall.","A second set of footsteps follows yours.",
 "Something knocks three times beneath the floor.","A silhouette vanishes when you look at it.",
 "Your flashlight flickers. Something crossed in front of it.","A distant voice repeats your last message.",
 "Every sound in the world stops for a moment.","A door opens somewhere, but there are no doors nearby.",
 "A low growl comes from directly above you.","Something scratches at stone behind you.",
 "A child's laugh echoes through the cave.","Your own footsteps approach from the darkness.",
 "A shadow moves against the direction of the light.","The cave just got quieter. That is not good.",
 "A heartbeat thumps nearby. It is much too slow.","A minecart rolls on a track that does not exist.",
 "A voice whispers: I can see your name.","Something splashes nearby. Nothing is there.",
 "A heavy object drags across the ground behind you.","A familiar voice calls from a dark tunnel.",
 "The air turns cold. Something is standing close.","A pair of eyes glints in the dark, then disappears.",
 "Three knocks answer from far underground.","You hear stone breaking, one block at a time.",
 "A distant scream cuts off before it finishes.","Something runs past you. You never see it.",
 "Your name is whispered from the wrong direction.","A shadow briefly covers the moon.",
 "The darkness moves when you stop moving.","A soft humming follows you from room to room.",
 "Claws tap against the ceiling.","A second heartbeat starts beating beside yours.",
 "Something exhales right behind your ear.","A faraway bell rings once. No village is nearby.",
 "The cave echoes with a scream that sounds like you.","A figure stands still at the end of the tunnel.",
 "You hear a torch being placed, but no one is there.","A slow, wet sound comes from the darkness below.",
 "Something taps on the back of your helmet.","The wind whispers: do not go back.",
 "A low laugh follows the sound of your inventory opening.","Breathing stops the instant you turn around.",
 "A shape crawls across the ceiling above you.","A voice says: that is not the way out.",
 "A door slams in a place you have never visited.","The darkness behind you feels crowded.",
 "A distant roar shakes the cave. Dust falls.","Something whispers the number of this day.",
 "A familiar voice says: I found you.","A tall figure stands inside your shadow for one second."
 };
 public static void tick(ServerWorld w){
  if(w.getTime()%20!=0)return;
  for(ServerPlayerEntity p:w.getPlayers()){
   if(p.isSpectator())continue;
   int t=CLOCKS.getOrDefault(p.getUuid(),900+R.nextInt(1800))-1;
   if(t>0){CLOCKS.put(p.getUuid(),t);continue;}
   CLOCKS.put(p.getUuid(),900+R.nextInt(1800));
   if(R.nextInt(100)<22)continue;
   int id=R.nextInt(EVENTS.length);
   p.sendMessage(Text.literal("[ UNKNOWN ] "+EVENTS[id]).formatted(Formatting.DARK_RED),false);
   switch(id%6){
    case 0 -> p.playSound(SoundEvents.ENTITY_WARDEN_HEARTBEAT,.8f,.55f+R.nextFloat()*.35f);
    case 1 -> {p.playSound(SoundEvents.BLOCK_STONE_STEP,.9f,.45f);p.playSound(SoundEvents.BLOCK_STONE_STEP,.9f,.45f);}
    case 2 -> {p.addStatusEffect(new StatusEffectInstance(StatusEffects.DARKNESS,50,0,false,false,false));p.playSound(SoundEvents.ENTITY_WARDEN_NEARBY_CLOSE,.8f,.6f);}
    case 3 -> {p.addStatusEffect(new StatusEffectInstance(StatusEffects.BLINDNESS,18,0,false,false,false));p.playSound(SoundEvents.ENTITY_ENDERMAN_STARE,.65f,.5f);}
    case 4 -> {BlockPos b=p.getBlockPos();w.spawnParticles(ParticleTypes.SMOKE,b.getX()+.5,b.getY()+1,b.getZ()+.5,18,1.2,.7,1.2,.015);p.playSound(SoundEvents.ENTITY_VEX_AMBIENT,.8f,.5f);}
    default -> {Vec3d v=p.getRotationVec(1).multiply(-1,0,-1).normalize().multiply(4);w.playSound(null,p.getX()+v.x,p.getY(),p.getZ()+v.z,SoundEvents.ENTITY_ZOMBIE_AMBIENT,SoundCategory.AMBIENT,.9f,.45f);}
   }
  }
 }
}
"""
(root / "HorrorEvents.java").write_text(horror_events, encoding="utf-8")

# Enable the 50-event system and make the Dweller appear in real cave spaces.
replace("DreadDirector.java", "        CorisandeManager.tick(world);", "        CorisandeManager.tick(world);\n        HorrorEvents.tick(world);")
replace("DreadDirector.java", "int natural = NATURAL_SPAWN_TIMERS.getOrDefault(p.getUuid(), 2200 + R.nextInt(2600)) - 1;", "int natural = NATURAL_SPAWN_TIMERS.getOrDefault(p.getUuid(), 900 + R.nextInt(900)) - 1;")
replace("DreadDirector.java", "NATURAL_SPAWN_TIMERS.put(p.getUuid(), 2200 + R.nextInt(2600));", "NATURAL_SPAWN_TIMERS.put(p.getUuid(), 900 + R.nextInt(900));")
replace("DreadDirector.java", "if (roll < 65) spawn(w, p, FromTheHorror.DWELLER, 24, 38);", "if (roll < 82) spawnCaveDweller(w, p);")
replace("DreadDirector.java", "    private static void fog(ServerWorld w, ServerPlayerEntity p) {", """    private static void spawnCaveDweller(ServerWorld w, ServerPlayerEntity p) {
        BlockPos base = p.getBlockPos();
        if (w.isSkyVisible(base) || base.getY() > 48) return;
        if (!w.getEntitiesByClass(HostileEntity.class, p.getBoundingBox().expand(112), e -> e.getType() == FromTheHorror.DWELLER).isEmpty()) return;
        for (int i = 0; i < 24; i++) {
            double a = R.nextDouble() * Math.PI * 2;
            int d = 22 + R.nextInt(25), x = base.getX() + (int)(Math.cos(a)*d), z = base.getZ() + (int)(Math.sin(a)*d);
            int y = base.getY() + R.nextInt(17) - 8;
            BlockPos at = new BlockPos(x,y,z);
            if (!w.isChunkLoaded(at) || w.isSkyVisible(at) || w.getLightLevel(at) > 7) continue;
            if (!w.getBlockState(at).isAir() || !w.getBlockState(at.up()).isAir() || !w.getBlockState(at.up(2)).isAir()) continue;
            if (!w.getBlockState(at.down()).isSolidBlock(w,at.down())) continue;
            DwellerEntity mob = FromTheHorror.DWELLER.create(w);
            if (mob == null) return;
            mob.refreshPositionAndAngles(x+.5,y,z+.5,R.nextFloat()*360f,0);
            w.spawnEntity(mob);
            return;
        }
    }

    private static void fog(ServerWorld w, ServerPlayerEntity p) {""")
# Corisande's transformed form gets a much larger hitbox, model scale, and heavier damage.
replace("CorisandeEntity.java", "return isHostile() ? EntityDimensions.fixed(1.6f, 1.8f) : super.getDimensions(pose);", "return isHostile() ? EntityDimensions.fixed(3.2f, 4.8f) : super.getDimensions(pose);")
replace("CorisandeEntity.java", ".add(EntityAttributes.GENERIC_ATTACK_DAMAGE, 8.0)", ".add(EntityAttributes.GENERIC_ATTACK_DAMAGE, 18.0)")
replace("CorisandeEntity.java", "this.getAttributeInstance(EntityAttributes.GENERIC_FLYING_SPEED).setBaseValue(0.75);", "this.getAttributeInstance(EntityAttributes.GENERIC_FLYING_SPEED).setBaseValue(0.95);\n        this.getAttributeInstance(EntityAttributes.GENERIC_MOVEMENT_SPEED).setBaseValue(0.48);\n        this.getAttributeInstance(EntityAttributes.GENERIC_ATTACK_DAMAGE).setBaseValue(18.0);")
replace("CorisandeEntity.java", "this.getNavigation().startMovingTo(p.getX(), p.getY() + 0.8, p.getZ(), 1.4);", "this.getNavigation().startMovingTo(p.getX(), p.getY() + 1.8, p.getZ(), 1.65);")
replace("client/CorisandeRenderer.java", "float s = e.isHostile() ? 2.6f : 1.3f;\n        m.scale(s, s, s);", "if (e.isHostile()) m.scale(4.6f, 4.6f, 4.6f);\n        else m.scale(1.3f, 1.3f, 1.3f);")
replace("CorisandeManager.java", '"Five days. I told you something was coming."', '"The fifth day is over. Day and night, five times. Now you see what I really am."')

import shutil
shared = Path(__file__).parent / "src/main/java/com/fromthehorror/HorrorMobEntity.java"
shutil.copyfile(shared, root / "HorrorMobEntity.java")
