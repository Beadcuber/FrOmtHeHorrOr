from pathlib import Path
import json, sys, shutil

project = Path(sys.argv[1])
java = project / "src/main/java/com/fromthehorror"
client = java / "client"

def edit(path, old, new):
    p = path
    s = p.read_text(encoding="utf-8")
    if old not in s:
        raise SystemExit("Missing patch target in " + str(p) + ": " + old[:90])
    p.write_text(s.replace(old, new, 1), encoding="utf-8")

# Three genuinely registered, renderable hostile entity types.
mob = r'''package com.fromthehorror;
import net.minecraft.entity.EntityType;
import net.minecraft.entity.attribute.DefaultAttributeContainer;
import net.minecraft.entity.attribute.EntityAttributes;
import net.minecraft.entity.effect.StatusEffectInstance;
import net.minecraft.entity.effect.StatusEffects;
import net.minecraft.entity.mob.HostileEntity;
import net.minecraft.entity.player.PlayerEntity;
import net.minecraft.server.world.ServerWorld;
import net.minecraft.sound.SoundCategory;
import net.minecraft.sound.SoundEvents;
import net.minecraft.text.Text;
import net.minecraft.world.World;

public class HorrorMobEntity extends HostileEntity {
    private int life = 7200;
    private int specialCooldown = 100;
    public HorrorMobEntity(EntityType<? extends HostileEntity> type, World world) {
        super(type, world);
        setPersistent();
        String name = type == FromTheHorror.LURKER ? "The Lurker" :
                type == FromTheHorror.MIMIC ? "The Mimic" : "The Screecher";
        setCustomName(Text.literal(name));
        setCustomNameVisible(true);
    }
    public static DefaultAttributeContainer.Builder createAttributes() {
        return HostileEntity.createHostileAttributes()
                .add(EntityAttributes.GENERIC_MAX_HEALTH, 46.0)
                .add(EntityAttributes.GENERIC_MOVEMENT_SPEED, 0.31)
                .add(EntityAttributes.GENERIC_ATTACK_DAMAGE, 8.0)
                .add(EntityAttributes.GENERIC_FOLLOW_RANGE, 72.0);
    }
    @Override public void tick() {
        super.tick();
        if (getWorld().isClient) return;
        if (--life <= 0) { discard(); return; }
        PlayerEntity target = getWorld().getClosestPlayer(this, 72.0);
        if (target == null || target.isSpectator()) return;
        double distance = distanceTo(target);
        if (--specialCooldown <= 0) {
            specialCooldown = 120 + random.nextInt(160);
            if (getType() == FromTheHorror.MIMIC && distance > 8 && distance < 36 && getWorld() instanceof ServerWorld server) {
                double angle = target.getYaw() * Math.PI / 180.0;
                requestTeleport(target.getX() - Math.sin(angle) * 9.0, target.getY(), target.getZ() + Math.cos(angle) * 9.0);
                server.playSound(null, getBlockPos(), SoundEvents.ENTITY_ENDERMAN_TELEPORT, SoundCategory.HOSTILE, 0.8f, 0.55f);
            } else if (getType() == FromTheHorror.SCREECHER && distance < 14) {
                target.addStatusEffect(new StatusEffectInstance(StatusEffects.DARKNESS, 70));
                getWorld().playSound(null, getBlockPos(), SoundEvents.ENTITY_WARDEN_SONIC_BOOM, SoundCategory.HOSTILE, 0.75f, 0.55f);
            } else if (getType() == FromTheHorror.LURKER && distance < 30) {
                getWorld().playSound(null, getBlockPos(), SoundEvents.ENTITY_WARDEN_HEARTBEAT, SoundCategory.HOSTILE, 0.65f, 0.5f);
            }
        }
        if (distance < 2.2 && age % 20 == 0) tryAttack(target);
    }
}
'''
(java / "HorrorMobEntity.java").write_text(mob, encoding="utf-8")

p = java / "FromTheHorror.java"
edit(p, "    public static EntityType<CorisandeEntity> CORISANDE;\n", """    public static EntityType<CorisandeEntity> CORISANDE;
    public static EntityType<HorrorMobEntity> LURKER;
    public static EntityType<HorrorMobEntity> MIMIC;
    public static EntityType<HorrorMobEntity> SCREECHER;
""")
edit(p, """        FabricDefaultAttributeRegistry.register(CORISANDE, CorisandeEntity.createAttributes());
""", """        FabricDefaultAttributeRegistry.register(CORISANDE, CorisandeEntity.createAttributes());
        LURKER = Registry.register(Registries.ENTITY_TYPE, new Identifier(ID, "lurker"),
                FabricEntityTypeBuilder.create(SpawnGroup.MONSTER, HorrorMobEntity::new).dimensions(EntityDimensions.fixed(0.9f, 2.7f)).trackRangeBlocks(80).build());
        MIMIC = Registry.register(Registries.ENTITY_TYPE, new Identifier(ID, "mimic"),
                FabricEntityTypeBuilder.create(SpawnGroup.MONSTER, HorrorMobEntity::new).dimensions(EntityDimensions.fixed(0.8f, 2.2f)).trackRangeBlocks(80).build());
        SCREECHER = Registry.register(Registries.ENTITY_TYPE, new Identifier(ID, "screecher"),
                FabricEntityTypeBuilder.create(SpawnGroup.MONSTER, HorrorMobEntity::new).dimensions(EntityDimensions.fixed(1.1f, 3.0f)).trackRangeBlocks(80).build());
        FabricDefaultAttributeRegistry.register(LURKER, HorrorMobEntity.createAttributes());
        FabricDefaultAttributeRegistry.register(MIMIC, HorrorMobEntity.createAttributes());
        FabricDefaultAttributeRegistry.register(SCREECHER, HorrorMobEntity.createAttributes());
""")
edit(p, """        Item e4 = egg("corisande", CORISANDE, 0xff9628, 0x7a1010);
""", """        Item e4 = egg("corisande", CORISANDE, 0xff9628, 0x7a1010);
        Item e5 = egg("lurker", LURKER, 0x171313, 0x8c1d1d);
        Item e6 = egg("mimic", MIMIC, 0x252525, 0xb3a18b);
        Item e7 = egg("screecher", SCREECHER, 0x090909, 0x5b4c80);
""")
edit(p, "e.add(e1); e.add(e2); e.add(e3); e.add(e4);", "e.add(e1); e.add(e2); e.add(e3); e.add(e4); e.add(e5); e.add(e6); e.add(e7);")

# Admin commands for testing each new monster.
edit(p, """                    .then(CommandManager.literal("man").executes(c -> {
                        DreadDirector.spawn(c.getSource().getWorld(), c.getSource().getPlayerOrThrow(), MAN, 12, 16); return 1; }))""",
"""                    .then(CommandManager.literal("man").executes(c -> {
                        DreadDirector.spawn(c.getSource().getWorld(), c.getSource().getPlayerOrThrow(), MAN, 12, 16); return 1; }))
                    .then(CommandManager.literal("lurker").executes(c -> { DreadDirector.spawn(c.getSource().getWorld(), c.getSource().getPlayerOrThrow(), LURKER, 12, 18); return 1; }))
                    .then(CommandManager.literal("mimic").executes(c -> { DreadDirector.spawn(c.getSource().getWorld(), c.getSource().getPlayerOrThrow(), MIMIC, 12, 18); return 1; }))
                    .then(CommandManager.literal("screecher").executes(c -> { DreadDirector.spawn(c.getSource().getWorld(), c.getSource().getPlayerOrThrow(), SCREECHER, 12, 18); return 1; }))""")

# Give each monster its own model layer and reuse the hand-painted base mesh with tinted textures.
layers = client / "NfLayers.java"
edit(layers, "    public static final EntityModelLayer ORB =", """    public static final EntityModelLayer LURKER = new EntityModelLayer(new Identifier(FromTheHorror.ID, "lurker"), "main");
    public static final EntityModelLayer MIMIC = new EntityModelLayer(new Identifier(FromTheHorror.ID, "mimic"), "main");
    public static final EntityModelLayer SCREECHER = new EntityModelLayer(new Identifier(FromTheHorror.ID, "screecher"), "main");
    public static final EntityModelLayer ORB =""")
layers_java = client / "Layers.java"
edit(layers_java, "    public static TexturedModelData orb() {", """    public static TexturedModelData lurker() { return dweller(); }
    public static TexturedModelData mimic() { return watcher(); }
    public static TexturedModelData screecher() { return man(); }

    public static TexturedModelData orb() {""")
cl = client / "FromTheHorrorClient.java"
edit(cl, "        EntityModelLayerRegistry.registerModelLayer(NfLayers.ORB, OrbModel::build);", """        EntityModelLayerRegistry.registerModelLayer(NfLayers.ORB, OrbModel::build);
        EntityModelLayerRegistry.registerModelLayer(NfLayers.LURKER, () -> Layers.lurker());
        EntityModelLayerRegistry.registerModelLayer(NfLayers.MIMIC, () -> Layers.mimic());
        EntityModelLayerRegistry.registerModelLayer(NfLayers.SCREECHER, () -> Layers.screecher());""")
edit(cl, "        EntityRendererRegistry.register(FromTheHorror.CORISANDE, CorisandeRenderer::new);", """        EntityRendererRegistry.register(FromTheHorror.CORISANDE, CorisandeRenderer::new);
        EntityRendererRegistry.register(FromTheHorror.LURKER, ctx -> new FigureRenderer<>(ctx, NfLayers.LURKER, FigureModel.DWELLER, "lurker", 1.45f));
        EntityRendererRegistry.register(FromTheHorror.MIMIC, ctx -> new FigureRenderer<>(ctx, NfLayers.MIMIC, FigureModel.WATCHER, "mimic", 1.15f));
        EntityRendererRegistry.register(FromTheHorror.SCREECHER, ctx -> new FigureRenderer<>(ctx, NfLayers.SCREECHER, FigureModel.MAN, "screecher", 1.35f));""")

# Natural encounters: Lurker in deep caves, Mimic in unlit places, Screecher at night.
director = java / "DreadDirector.java"
edit(director, """        if (underground) {
            if (roll < 65) spawn(w, p, FromTheHorror.DWELLER, 24, 38);
            else if (roll < 80 && nightOrStorm) spawn(w, p, FromTheHorror.MAN, 30, 44);
        } else if (nightOrStorm) {""", """        if (underground) {
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
        /*old natural spawn branch removed below*/
        if (false) {""")
# Remove now-obsolete duplicate branch tail introduced by replacement.
edit(director, """        } else if (nightOrStorm) {
            if (roll < 45) spawn(w, p, FromTheHorror.WATCHER, 30, 46);
            else if (roll < 85) spawn(w, p, FromTheHorror.MAN, 28, 42);
        } else if (roll < 8) {
            spawn(w, p, FromTheHorror.MAN, 32, 48);
        }
        // Corisande""", """        }
        // Corisande""")

# Texture variants are derived from the existing mod art, preserving transparency and UV layout.
try:
    from PIL import Image, ImageEnhance
    tex = project / "src/main/resources/assets/fromthehorror/textures/entity"
    variants = [("dweller.png","lurker.png",(0.62,0.28,0.30)),("watcher.png","mimic.png",(0.55,0.58,0.48)),("man_from_the_fog.png","screecher.png",(0.42,0.34,0.62))]
    for src,dst,tint in variants:
        im=Image.open(tex/src).convert("RGBA")
        px=im.load()
        for y in range(im.height):
            for x in range(im.width):
                r,g,b,a=px[x,y]
                if a: px[x,y]=(int(r*tint[0]),int(g*tint[1]),int(b*tint[2]),a)
        im.save(tex/dst)
    for src,dst in [("dweller_eyes.png","lurker_eyes.png"),("watcher_eyes.png","mimic_eyes.png"),("man_from_the_fog_eyes.png","screecher_eyes.png")]:
        shutil.copyfile(tex/src,tex/dst)
except Exception as e:
    raise SystemExit("Could not create monster textures: "+str(e))

lang = project / "src/main/resources/assets/fromthehorror/lang/en_us.json"
data=json.loads(lang.read_text(encoding="utf-8"))
data.update({
 "item.fromthehorror.lurker_spawn_egg":"Lurker Spawn Egg",
 "item.fromthehorror.mimic_spawn_egg":"Mimic Spawn Egg",
 "item.fromthehorror.screecher_spawn_egg":"Screecher Spawn Egg",
 "entity.fromthehorror.lurker":"The Lurker",
 "entity.fromthehorror.mimic":"The Mimic",
 "entity.fromthehorror.screecher":"The Screecher"
})
lang.write_text(json.dumps(data,indent=2)+"\n",encoding="utf-8")

print("Registered and rendered The Lurker, The Mimic, and The Screecher; added spawn eggs, commands, textures, and natural encounters.")
