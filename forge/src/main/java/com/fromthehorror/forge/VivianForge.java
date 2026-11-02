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

@Mod(VivianForge.MOD_ID)
public final class VivianForge {
    public static final String MOD_ID = "vivian";
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
        if (event.getTabKey() == CreativeModeTabs.TOOLS) event.accept(FLASHLIGHT);
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
            .then(Commands.argument("message", StringArgumentType.greedyString()).executes(ctx -> {
                ctx.getSource().sendSuccess(() -> Component.literal("<Vivian> I hear you. I'm still learning how to answer that."), false); return 1;
            })));
    }
    @SubscribeEvent public void onChat(ServerChatEvent event) {
        String text = event.getMessage().getString().toLowerCase(java.util.Locale.ROOT);
        if (text.startsWith("vivian")) event.getPlayer().sendSystemMessage(Component.literal("<Vivian> I hear you."));
    }
}
