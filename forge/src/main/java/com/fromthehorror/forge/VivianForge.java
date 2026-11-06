package com.fromthehorror.forge;

import com.mojang.brigadier.arguments.StringArgumentType;
import net.minecraft.commands.Commands;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.item.CreativeModeTabs;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.SpawnEggItem;
import net.minecraftforge.common.MinecraftForge;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.event.ServerChatEvent;
import net.minecraftforge.event.entity.EntityAttributeCreationEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;
import net.minecraftforge.event.BuildCreativeModeTabContentsEvent;
import net.minecraftforge.eventbus.api.IEventBus;

import java.util.Locale;
import java.util.Set;
import java.util.regex.Pattern;

@Mod(VivianForge.MOD_ID)
public final class VivianForge {
    public static final String MOD_ID = "vivian";
    private static final String ANGER_KEY = "VivianAnger";
    private static final String CHAT_COUNT_KEY = "VivianChatCount";
    private static final Pattern WORDS = Pattern.compile("[a-z']+");
    private static final Set<String> STRONG_INSULTS = Set.of(
        "hate", "stupid", "idiot", "dumb", "ugly", "annoying", "worthless",
        "useless", "shut", "loser", "freak", "pathetic", "trash", "garbage"
    );
    private static final Set<String> KIND_WORDS = Set.of(
        "like", "love", "friend", "nice", "good", "great", "cool", "awesome",
        "thanks", "thank", "sorry", "please", " appreciate", "trust"
    );

    public static final DeferredRegister<EntityType<?>> ENTITIES = DeferredRegister.create(ForgeRegistries.ENTITY_TYPES, MOD_ID);
    public static final DeferredRegister<Item> ITEMS = DeferredRegister.create(ForgeRegistries.ITEMS, MOD_ID);
    public static final RegistryObject<EntityType<VivianEntity>> VIVIAN = ENTITIES.register("vivian", () -> EntityType.Builder.of(VivianEntity::new, net.minecraft.world.entity.MobCategory.CREATURE).sized(0.7F, 0.7F).clientTrackingRange(10).build("vivian"));
    public static final RegistryObject<EntityType<VivianEntity>> VIVIAN_MONSTER = ENTITIES.register("vivian_monster", () -> EntityType.Builder.of(VivianEntity::new, net.minecraft.world.entity.MobCategory.MONSTER).sized(3.2F, 4.8F).clientTrackingRange(16).build("vivian_monster"));
    public static final RegistryObject<Item> FLASHLIGHT = ITEMS.register("flashlight", () -> new Item(new Item.Properties().stacksTo(1).durability(1200)));
    public static final RegistryObject<Item> VIVIAN_CARRY = ITEMS.register("vivian_carry", () -> new VivianCarryItem(new Item.Properties().stacksTo(1)));
    public static final RegistryObject<Item> VIVIAN_EGG = ITEMS.register("vivian_spawn_egg", () -> new SpawnEggItem(VIVIAN.get(), 0xff9628, 0x7a1010, new Item.Properties()));
    public static final RegistryObject<Item> MONSTER_EGG = ITEMS.register("vivian_monster_spawn_egg", () -> new SpawnEggItem(VIVIAN_MONSTER.get(), 0x120b12, 0x9b111f, new Item.Properties()));

    public VivianForge() {
        IEventBus modBus = FMLJavaModLoadingContext.get().getModEventBus();
        ENTITIES.register(modBus); ITEMS.register(modBus);
        modBus.addListener(this::registerAttributes);
        modBus.addListener(this::addCreativeItems);
        MinecraftForge.EVENT_BUS.register(this);
    }
    private void registerAttributes(EntityAttributeCreationEvent event) {
        event.put(VIVIAN.get(), VivianEntity.createAttributes().build());
        event.put(VIVIAN_MONSTER.get(), VivianEntity.createAttributes().build());
    }
    private void addCreativeItems(BuildCreativeModeTabContentsEvent event) {
        if (event.getTabKey() == CreativeModeTabs.TOOLS_AND_UTILITIES) event.accept(FLASHLIGHT);
        if (event.getTabKey() == CreativeModeTabs.SPAWN_EGGS) { event.accept(VIVIAN_EGG); event.accept(MONSTER_EGG); }
        if (event.getTabKey() == CreativeModeTabs.FUNCTIONAL_BLOCKS) event.accept(VIVIAN_CARRY);
    }
    @SubscribeEvent public void onPlayerJoin(PlayerEvent.PlayerLoggedInEvent event) {
        if (!(event.getEntity() instanceof ServerPlayer player)) return;
        if (!player.getTags().contains("vivian_received_starting_flashlight")) {
            var stack = new net.minecraft.world.item.ItemStack(FLASHLIGHT.get());
            if (!player.getInventory().add(stack)) player.drop(stack, false);
            player.addTag("vivian_received_starting_flashlight");
            player.sendSystemMessage(Component.literal("You received a flashlight. Keep it close."));
        }
    }
    @SubscribeEvent public void onCommands(RegisterCommandsEvent event) {
        event.getDispatcher().register(Commands.literal("vivian")
            .then(Commands.literal("summon").executes(ctx -> {
                ServerPlayer player = ctx.getSource().getPlayerOrException();
                VivianEntity entity = VIVIAN.get().create(player.serverLevel());
                if (entity == null) return 0;
                entity.moveTo(player.getX() + 2, player.getY() + 1, player.getZ() + 2, player.getYRot(), 0);
                player.serverLevel().addFreshEntity(entity);
                player.sendSystemMessage(Component.literal("<Vivian> You called?")); return 1;
            }))
            .then(Commands.literal("monster").requires(src -> src.hasPermission(2)).executes(ctx -> {
                ServerPlayer player = ctx.getSource().getPlayerOrException();
                VivianEntity entity = VIVIAN_MONSTER.get().create(player.serverLevel());
                if (entity == null) return 0;
                entity.setHostile(true);
                entity.moveTo(player.getX() + 3, player.getY(), player.getZ() + 3, player.getYRot(), 0);
                player.serverLevel().addFreshEntity(entity);
                player.sendSystemMessage(Component.literal("<Vivian> Now run.")); return 1;
            }))
            .then(Commands.literal("anger").executes(ctx -> {
                ServerPlayer player = ctx.getSource().getPlayerOrException();
                player.sendSystemMessage(Component.literal("<Vivian> My anger: " + anger(player) + "/100"));
                return 1;
            }))
            .then(Commands.argument("message", StringArgumentType.greedyString()).executes(ctx -> {
                ServerPlayer player = ctx.getSource().getPlayerOrException();
                String reply = talk(player, StringArgumentType.getString(ctx, "message"));
                player.sendSystemMessage(Component.literal("<Vivian> " + reply));
                return 1;
            })));
    }

    @SubscribeEvent public void onChat(ServerChatEvent event) {
        ServerPlayer player = event.getPlayer();
        String message = event.getMessage().getString();
        boolean nearby = !player.serverLevel().getEntitiesOfClass(VivianEntity.class,
            player.getBoundingBox().inflate(24), e -> !e.isHostile()).isEmpty();
        if (!nearby && !message.toLowerCase(Locale.ROOT).contains("vivian")) return;
        String reply = talk(player, message);
        player.sendSystemMessage(Component.literal("<Vivian> " + reply));
    }

    private static int anger(ServerPlayer player) {
        return player.getPersistentData().getInt(ANGER_KEY);
    }

    private static String talk(ServerPlayer player, String raw) {
        String s = raw.toLowerCase(Locale.ROOT).replaceAll("[^a-z0-9' ]", " ").replaceAll("\\s+", " ").trim();
        if (s.isEmpty()) return "I didn't catch that. Say it again?";

        boolean negatedLike = s.matches(".*\\b(don't|dont|do not|can't|cant|cannot)\\s+(like|love|want)\\b.*");
        boolean directHate = s.matches(".*\\b(i|you)\\s+.*\\bhate\\b.*") || s.matches(".*\\bhate\\s+you\\b.*");
        boolean apology = containsAny(s, "sorry", "my bad", "forgive", "didn't mean", "didnt mean");
        boolean kindness = containsAny(s, "i like you", "i love you", "you're my friend", "you are my friend", "good job", "thank you", "thanks vivian");
        boolean insult = containsAny(s, "stupid", "idiot", "dumb", "ugly", "annoying", "worthless", "useless", "shut up", "loser", "pathetic", "trash", "garbage", "i hate", "hate you", "don't like you", "dont like you", "i dislike you", "go away");

        int current = anger(player);
        if (apology) {
            current = Math.max(0, current - 28);
            player.getPersistentData().putInt(ANGER_KEY, current);
            return current == 0 ? "…Okay. I'm trying to forgive you. Just don't keep doing it." : "I'm still upset, but I heard your apology. Anger: " + current + "/100.";
        }
        if (directHate || insult || negatedLike) {
            int increase = directHate ? 28 : (negatedLike ? 22 : 16);
            current = Math.min(100, current + increase);
            player.getPersistentData().putInt(ANGER_KEY, current);
            if (current >= 75) {
                turnHostile(player);
                return "THAT'S ENOUGH. I trusted you. Now stay away from me.";
            }
            if (current >= 45) return "You keep saying things like that… I'm done being nice. Anger: " + current + "/100.";
            if (current >= 20) return "That actually hurt. I'm getting angry with you. Anger: " + current + "/100.";
            return "Wait… you really mean that? That wasn't very nice. Anger: " + current + "/100.";
        }
        if (kindness) {
            current = Math.max(0, current - 10);
            player.getPersistentData().putInt(ANGER_KEY, current);
            return current > 0 ? "That means something. I'm calming down… Anger: " + current + "/100." : "Really? That makes me happy. You're my friend too.";
        }

        player.getPersistentData().putInt(CHAT_COUNT_KEY, player.getPersistentData().getInt(CHAT_COUNT_KEY) + 1);
        if (containsAny(s, "hello", "hi vivian", "hey vivian", "hey", "good morning", "good night")) return pick(player, "Hey! I was hoping you'd talk to me.", "Oh, hi! What's going on?", "Hello again. What are we doing today?");
        if (containsAny(s, "how are you", "how do you feel", "you okay", "are you okay")) return current >= 30 ? "Honestly? Not great. You haven't exactly been kind to me." : pick(player, "I'm doing pretty well now that you're here.", "A little restless. Want to explore?", "I'm okay. How are you holding up?");
        if (containsAny(s, "what are you", "who are you", "your name")) return "I'm Vivian. I'm not just some item or mob, you know. I'm your companion.";
        if (containsAny(s, "follow me", "come here", "stay here", "wait here")) return containsAny(s, "stay", "wait") ? "Okay. I'll stay close to this spot." : "Got it. I'll stick with you.";
        if (containsAny(s, "help", "protect me", "scared", "monster", "creeper", "zombie")) return "Stay behind me if something comes. Keep your flashlight ready, too.";
        if (containsAny(s, "where", "village", "house", "structure")) return "I can look around with you. Tell me what direction you want to go.";
        if (containsAny(s, "why", "what", "when", "where", "who", "how", "can you", "do you")) return pick(player, "Hmm… let me think about that. Can you tell me a little more?", "I don't know for sure, but I'll help you figure it out.", "That's a good question. What do you think?");
        if (containsAny(s, "thank", "thx")) return "You're welcome! I'm glad I could help.";
        if (containsAny(s, "goodbye", "bye", "see you")) return "Don't be gone too long, okay?";
        if (containsAny(s, "boring", "bored")) return "We could explore, build something, or go looking for trouble. Your choice.";
        if (containsAny(s, " minecraft", "survival", "creative", "nether", "ender dragon", "diamonds", "mining", "craft")) return "Minecraft's a strange place. Keep your gear ready and watch the dark.";
        return pick(player, "I hear you. Tell me more.", "I'm listening. What happened next?", "I'm not sure what you mean yet, but I want to understand.", "Oh? Why do you say that?", "Let's figure it out together.");
    }

    private static boolean containsAny(String text, String... phrases) {
        for (String phrase : phrases) if (text.contains(phrase.trim())) return true;
        return false;
    }

    private static String pick(ServerPlayer player, String... choices) {
        long seed = player.getUUID().getLeastSignificantBits() ^ player.serverLevel().getGameTime() ^ player.getPersistentData().getInt(CHAT_COUNT_KEY);
        return choices[Math.floorMod((int)(seed ^ (seed >>> 32)), choices.length)];
    }

    private static void turnHostile(ServerPlayer player) {
        var nearby = player.serverLevel().getEntitiesOfClass(VivianEntity.class, player.getBoundingBox().inflate(32), e -> !e.isHostile());
        if (!nearby.isEmpty()) nearby.get(0).setHostile(true);
    }
}
