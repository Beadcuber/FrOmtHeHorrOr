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



# Final release content: seven additional hostile types, structures, and mood achievements.
from pathlib import Path
import json, shutil
from PIL import Image
r=Path(sys.argv[1]); j=r/"src/main/java/com/fromthehorror"
p=j/"FromTheHorror.java"; s=p.read_text()
mobs=[("HOLLOW","hollow"),("STALKER","stalker"),("GRINNER","grinner"),("PALE_ONE","pale_one"),("CRAWLER","crawler"),("SIREN","siren"),("RAVEN","raven")]
s=s.replace("    public static EntityType<HorrorMobEntity> SCREECHER;\n","    public static EntityType<HorrorMobEntity> SCREECHER;\n"+"".join(f"    public static EntityType<HorrorMobEntity> {a};\n" for a,b in mobs))
regs="".join(f'''        {a} = Registry.register(Registries.ENTITY_TYPE, new Identifier(ID, "{b}"), FabricEntityTypeBuilder.create(SpawnGroup.MONSTER, HorrorMobEntity::new).dimensions(EntityDimensions.fixed(0.8f,2.4f)).trackRangeBlocks(88).build());
        FabricDefaultAttributeRegistry.register({a}, HorrorMobEntity.createAttributes());
''' for a,b in mobs)
s=s.replace("        FabricDefaultAttributeRegistry.register(SCREECHER, HorrorMobEntity.createAttributes());\n","        FabricDefaultAttributeRegistry.register(SCREECHER, HorrorMobEntity.createAttributes());\n"+regs)
eggs="".join(f'        Item egg_{b}=egg("{b}",{a},0x171313,0x{c:06x});\n' for (a,b),c in zip(mobs,[0x9b2424,0x292b38,0x6f1717,0xb8b8b8,0x392b25,0x334b63,0x171717]))
s=s.replace('        Item e7 = egg("screecher", SCREECHER, 0x090909, 0x5b4c80);\n','        Item e7 = egg("screecher", SCREECHER, 0x090909, 0x5b4c80);\n'+eggs)
s=s.replace('e.add(e7);','e.add(e7); '+''.join(f'e.add(egg_{b}); ' for a,b in mobs))
cmd="".join(f'                    .then(CommandManager.literal("{b}").executes(c -> {{ DreadDirector.spawn(c.getSource().getWorld(), c.getSource().getPlayerOrThrow(), {a}, 14, 22); return 1; }}))\n' for a,b in mobs)
s=s.replace('                    .then(CommandManager.literal("screecher").executes(c -> { DreadDirector.spawn(c.getSource().getWorld(), c.getSource().getPlayerOrThrow(), SCREECHER, 12, 18); return 1; }))\n','                    .then(CommandManager.literal("screecher").executes(c -> { DreadDirector.spawn(c.getSource().getWorld(), c.getSource().getPlayerOrThrow(), SCREECHER, 12, 18); return 1; }))\n'+cmd)
p.write_text(s)
# Seven distinct entity names and distinct status-effect powers.
p=j/"HorrorMobEntity.java"; s=p.read_text()
s=s.replace('''String name = type == FromTheHorror.LURKER ? "The Lurker" :
                type == FromTheHorror.MIMIC ? "The Mimic" : "The Screecher";''','''String name = type == FromTheHorror.LURKER ? "The Lurker" : type == FromTheHorror.MIMIC ? "The Mimic" :
                type == FromTheHorror.SCREECHER ? "The Screecher" : type == FromTheHorror.HOLLOW ? "The Hollow" :
                type == FromTheHorror.STALKER ? "The Stalker" : type == FromTheHorror.GRINNER ? "The Grinner" :
                type == FromTheHorror.PALE_ONE ? "The Pale One" : type == FromTheHorror.CRAWLER ? "The Crawler" :
                type == FromTheHorror.SIREN ? "The Siren" : "The Raven";''')
s=s.replace('''            } else if (getType() == FromTheHorror.LURKER && distance < 30) {
                getWorld().playSound(null, getBlockPos(), SoundEvents.ENTITY_WARDEN_HEARTBEAT, SoundCategory.HOSTILE, 0.65f, 0.5f);
            }''','''            } else if (getType() == FromTheHorror.LURKER && distance < 30) {
                getWorld().playSound(null, getBlockPos(), SoundEvents.ENTITY_WARDEN_HEARTBEAT, SoundCategory.HOSTILE, 0.65f, 0.5f);
            } else if (getType() == FromTheHorror.HOLLOW && distance < 18) target.addStatusEffect(new StatusEffectInstance(StatusEffects.WEAKNESS,100));
            else if (getType() == FromTheHorror.STALKER && distance < 24) target.addStatusEffect(new StatusEffectInstance(StatusEffects.SLOWNESS,80,1));
            else if (getType() == FromTheHorror.GRINNER && distance < 12) target.addStatusEffect(new StatusEffectInstance(StatusEffects.BLINDNESS,50));
            else if (getType() == FromTheHorror.PALE_ONE && distance < 20) target.addStatusEffect(new StatusEffectInstance(StatusEffects.MINING_FATIGUE,100));
            else if (getType() == FromTheHorror.CRAWLER && distance < 10) target.addStatusEffect(new StatusEffectInstance(StatusEffects.POISON,50));
            else if (getType() == FromTheHorror.SIREN && distance < 22) { target.addStatusEffect(new StatusEffectInstance(StatusEffects.NAUSEA,100)); getWorld().playSound(null,getBlockPos(),SoundEvents.ENTITY_GHAST_SCREAM,SoundCategory.HOSTILE,.8f,.6f); }
            else if (getType() == FromTheHorror.RAVEN && distance < 16) target.addStatusEffect(new StatusEffectInstance(StatusEffects.DARKNESS,60));''')
p.write_text(s)
# Reuse compatible baked meshes, but each mob has its own texture/renderer.
p=j/"client/FromTheHorrorClient.java"; s=p.read_text()
renders="".join(f'        EntityRendererRegistry.register(FromTheHorror.{a}, ctx -> new FigureRenderer<>(ctx, NfLayers.{layer}, FigureModel.{model}, "{b}", {scale}f));\n' for (a,b,layer,model,scale) in [
("HOLLOW","hollow","LURKER","DWELLER","1.3"),("STALKER","stalker","MIMIC","WATCHER","1.1"),("GRINNER","grinner","SCREECHER","MAN","1.25"),("PALE_ONE","pale_one","LURKER","DWELLER","1.4"),("CRAWLER","crawler","MIMIC","WATCHER","1.2"),("SIREN","siren","SCREECHER","MAN","1.15"),("RAVEN","raven","MIMIC","WATCHER","1.0")])
s=s.replace('        EntityRendererRegistry.register(FromTheHorror.SCREECHER, ctx -> new FigureRenderer<>(ctx, NfLayers.SCREECHER, FigureModel.MAN, "screecher", 1.35f));\n','        EntityRendererRegistry.register(FromTheHorror.SCREECHER, ctx -> new FigureRenderer<>(ctx, NfLayers.SCREECHER, FigureModel.MAN, "screecher", 1.35f));\n'+renders); p.write_text(s)
tex=r/"src/main/resources/assets/fromthehorror/textures/entity"
for src,dst,tint in [("dweller.png","hollow.png",(0.5,.18,.18)),("watcher.png","stalker.png",(.18,.2,.35)),("man_from_the_fog.png","grinner.png",(.4,.12,.12)),("dweller.png","pale_one.png",(.8,.8,.8)),("watcher.png","crawler.png",(.3,.2,.12)),("man_from_the_fog.png","siren.png",(.18,.35,.55)),("watcher.png","raven.png",(.12,.12,.12))]:
 im=Image.open(tex/src).convert("RGBA"); px=im.load()
 for y in range(im.height):
  for x in range(im.width):
   rr,g,b,a=px[x,y]
   if a: px[x,y]=(int(rr*tint[0]),int(g*tint[1]),int(b*tint[2]),a)
 im.save(tex/dst); shutil.copyfile(tex/"watcher_eyes.png",tex/(dst[:-4]+"_eyes.png"))
lp=r/"src/main/resources/assets/fromthehorror/lang/en_us.json"; d=json.loads(lp.read_text())
for a,b in mobs: d["entity.fromthehorror."+b]="The "+b.replace("_"," ").title(); d["item.fromthehorror."+b+"_spawn_egg"]=b.replace("_"," ").title()+" Spawn Egg"
lp.write_text(json.dumps(d,indent=2)+"\n")
# Natural structures are deterministic per chunk, so they do not duplicate on chunk reload.
(j/"NaturalStructures.java").write_text("""package com.fromthehorror;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerChunkEvents;
import net.minecraft.block.Blocks;
import net.minecraft.server.world.ServerWorld;
import net.minecraft.world.Heightmap;
import net.minecraft.world.chunk.WorldChunk;
import net.minecraft.util.math.BlockPos;
public final class NaturalStructures {
 public static void register(){ServerChunkEvents.CHUNK_LOAD.register((world,chunk)->{place(world,chunk);});}
 private static void place(ServerWorld w,WorldChunk c){
  int x0=(c.getPos().x<<4)+8,z0=(c.getPos().z<<4)+8; long h=c.getPos().x*341873128712L+c.getPos().z*132897987541L; int pick=Math.floorMod((int)(h^(h>>>32)),401); if(pick>1)return;
  int y=w.getTopY(Heightmap.Type.WORLD_SURFACE,x0,z0); if(y<w.getBottomY()+2||y>w.getTopY()-12)return; BlockPos p=new BlockPos(x0,y,z0);
  if(pick==0){for(int x=-3;x<=3;x++)for(int z=-3;z<=3;z++)w.setBlockState(p.add(x,0,z),Blocks.OAK_PLANKS.getDefaultState(),3);
   for(int yy=1;yy<=4;yy++)for(int x=-3;x<=3;x++)for(int z=-3;z<=3;z++)if(Math.abs(x)==3||Math.abs(z)==3){if(!(z==3&&x==0&&yy<3))w.setBlockState(p.add(x,yy,z),(yy==4?Blocks.SPRUCE_LOG:Blocks.OAK_PLANKS).getDefaultState(),3);}
   for(int x=-3;x<=3;x++)for(int z=-3;z<=3;z++)if(Math.abs(x)+Math.abs(z)>=4)w.setBlockState(p.add(x,5,z),Blocks.DARK_OAK_PLANKS.getDefaultState(),3);
   w.setBlockState(p.add(1,1,1),Blocks.COBWEB.getDefaultState(),3);w.setBlockState(p.add(-1,1,-1),Blocks.COBWEB.getDefaultState(),3);w.setBlockState(p.add(0,1,0),Blocks.CHEST.getDefaultState(),3);
  }else{for(int x=-4;x<=4;x++)for(int z=-4;z<=4;z++)if(Math.abs(x)==4||Math.abs(z)==4)w.setBlockState(p.add(x,0,z),Blocks.CRYING_OBSIDIAN.getDefaultState(),3);
   for(int x=-2;x<=2;x++)for(int z=-2;z<=2;z++)w.setBlockState(p.add(x,0,z),Blocks.POLISHED_BLACKSTONE.getDefaultState(),3);
   for(int[] q:new int[][]{{-3,-3},{-3,3},{3,-3},{3,3}})for(int yy=1;yy<=3;yy++)w.setBlockState(p.add(q[0],yy,q[1]),Blocks.POLISHED_BLACKSTONE_BRICKS.getDefaultState(),3);
   w.setBlockState(p.up(),Blocks.REDSTONE_BLOCK.getDefaultState(),3);w.setBlockState(p.add(0,2,0),Blocks.CHAIN.getDefaultState(),3);w.setBlockState(p.add(0,3,0),Blocks.SOUL_LANTERN.getDefaultState(),3);
  }
 }
}
""")
# Mood achievements use vanilla impossible criteria granted when each anger/transform stage is reached.
(j/"MoodAdvancements.java").write_text("""package com.fromthehorror;
import net.minecraft.advancement.Advancement;
import net.minecraft.server.network.ServerPlayerEntity;
import net.minecraft.util.Identifier;
public final class MoodAdvancements { public static void grant(ServerPlayerEntity p,String id){Advancement a=p.getServer().getAdvancementLoader().get(new Identifier(FromTheHorror.ID,id));if(a!=null)p.getAdvancementTracker().grantCriterion(a,"mood");} }
""")
adv=r/"src/main/resources/data/fromthehorror/advancements"; adv.mkdir(parents=True,exist_ok=True)
for id,title,desc,frame in [("first_mood","Something Feels Off","Corisande is beginning to lose trust in you.","task"),("angry_mood","A Growing Anger","Push Corisande into a dangerous mood.","goal"),("furious_mood","The Point of No Return","Corisande warns that something is coming.","challenge"),("transformed_mood","From the Horror","Corisande has transformed.","challenge")]:
 (adv/(id+".json")).write_text(json.dumps({"display":{"icon":{"item":"minecraft:echo_shard"},"title":title,"description":desc,"frame":frame,"announce_to_chat":True,"show_toast":True},"criteria":{"mood":{"trigger":"minecraft:impossible"}}},indent=2)+"\n")
p=j/"CorisandeManager.java"; s=p.read_text()
s=s.replace("        st.anger = Math.min(100, st.anger + amt);\n        st.markDirty();","        int before=st.anger; st.anger = Math.min(100, st.anger + amt);\n        if(before<25 && st.anger>=25) MoodAdvancements.grant(p,\"first_mood\");\n        if(before<50 && st.anger>=50) MoodAdvancements.grant(p,\"angry_mood\");\n        st.markDirty();")
s=s.replace("        st.warned = true;\n        st.anger = 100;","        st.warned = true; MoodAdvancements.grant(p,\"furious_mood\");\n        st.anger = 100;")
s=s.replace("        if (st.warned && !st.turned && day >= st.madDay + COUNTDOWN_DAYS && w.isNight()) turnNow(w);","        if (st.warned && !st.turned && day >= st.madDay + COUNTDOWN_DAYS && w.isNight()) { MoodAdvancements.grant(p,\"transformed_mood\"); turnNow(w); }")
p.write_text(s)
p=j/"FromTheHorror.java"; s=p.read_text().replace("        ServerTickEvents.END_WORLD_TICK.register(DreadDirector::tick);","        ServerTickEvents.END_WORLD_TICK.register(DreadDirector::tick);\n        NaturalStructures.register();"); p.write_text(s)
print("Integrated 10 total added monsters, two natural structures, and four mood advancements.")
