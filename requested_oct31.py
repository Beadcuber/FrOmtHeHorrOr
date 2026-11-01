from pathlib import Path
r=Path("src/main/java/com/fromthehorror")
def patch(n,old,new):
 p=r/n;s=p.read_text()
 if old not in s: raise SystemExit("missing patch point: "+n)
 p.write_text(s.replace(old,new,1))
# Spawn the transformed form at the player's exact position after the third observed day-to-night transition.
patch("CorisandeManager.java",'''        st.turned = true;
        st.warned = true;
        st.markDirty();
        for (ServerPlayerEntity pl : w.getPlayers()) {
            say(pl, "Three day-to-night cycles have passed. Now you see what I really am.", true);
            say(pl, "It was me.", true);
            w.playSound(null, pl.getBlockPos(), SoundEvents.ENTITY_WITHER_SPAWN, SoundCategory.HOSTILE, 0.6f, 0.5f);
        }''','''        st.turned = true;
        st.warned = true;
        st.markDirty();
        ServerPlayerEntity target = w.getPlayers().isEmpty() ? null : w.getPlayers().get(0);
        if (target != null) {
            Entity old = st.entity == null ? null : w.getEntity(st.entity);
            if (old instanceof CorisandeEntity && !old.isRemoved()) old.discard();
            CorisandeEntity monster = FromTheHorror.CORISANDE_MONSTER.create(w);
            if (monster != null) {
                monster.refreshPositionAndAngles(target.getX(), target.getY(), target.getZ(), target.getYaw(), 0);
                monster.turn(); w.spawnEntity(monster); st.entity = monster.getUuid();
            }
        }
        for (ServerPlayerEntity pl : w.getPlayers()) {
            say(pl, "Three day-to-night cycles have passed. I found you. Now look at me.", true);
            say(pl, "It was me.", true);
            w.playSound(null, pl.getBlockPos(), SoundEvents.ENTITY_WITHER_SPAWN, SoundCategory.HOSTILE, 0.6f, 0.5f);
        }''')
# An apology is acknowledged, but it no longer instantly removes 25 anger.
patch("CorisandeBrain.java",'''            st.anger = Math.max(0, st.anger - 25);
            return "Thank you. Being angry makes the hunger louder.";''','''            return "I heard you. But saying sorry does not erase what happened. I need time, not just a word.";''')
# Monster form cannot be pushed or receive hit knockback.
p=r/"CorisandeEntity.java";s=p.read_text()
if "takeKnockback(double strength" not in s:
 s=s.replace("    @Override\n    public boolean damage(DamageSource source, float amount) {",'''    @Override public boolean isPushable() { return !isHostile() && super.isPushable(); }
    @Override public void takeKnockback(double strength, double x, double z) {
        if (!isHostile()) super.takeKnockback(strength, x, z);
    }
    @Override
    public boolean damage(DamageSource source, float amount) {''',1);p.write_text(s)
# Increase ambient encounter frequency and natural entity attempts to roughly every 15-30 seconds.
p=r/"DreadDirector.java";s=p.read_text()
s=s.replace("private static int nextDelay() { return 90 + R.nextInt(210); } // seconds","private static int nextDelay() { return 35 + R.nextInt(46); } // frequent scares")
s=s.replace("NATURAL_SPAWN_TIMERS.getOrDefault(p.getUuid(), 45 + R.nextInt(75)) - 1","NATURAL_SPAWN_TIMERS.getOrDefault(p.getUuid(), 15 + R.nextInt(16)) - 1")
s=s.replace("NATURAL_SPAWN_TIMERS.put(p.getUuid(), 45 + R.nextInt(75));","NATURAL_SPAWN_TIMERS.put(p.getUuid(), 15 + R.nextInt(16));")
# Detect the classic 3x3 gold + four redstone torches + netherrack + fire ritual.
s=s.replace("        CorisandeManager.tick(world);\n        HorrorEvents.tick(world);","        CorisandeManager.tick(world);\n        HorrorEvents.tick(world);\n        checkHerobrineRituals(world);",1)
ritual='''    private static final java.util.Set<Long> HEROBRINE_RITUALS = new java.util.HashSet<>();
    private static final java.util.Set<UUID> HEROBRINE_WARNED = new java.util.HashSet<>();
    private static void checkHerobrineRituals(ServerWorld w) {
        for (ServerPlayerEntity pl : w.getPlayers()) {
            BlockPos pp=pl.getBlockPos();
            for(int dx=-12;dx<=12;dx++) for(int dy=-4;dy<=4;dy++) for(int dz=-12;dz<=12;dz++) {
                BlockPos n=pp.add(dx,dy,dz);
                if(!w.getBlockState(n).isOf(net.minecraft.block.Blocks.NETHERRACK))continue;
                BlockPos b=n.down(); boolean gold=true;
                for(int x=-1;x<=1;x++)for(int z=-1;z<=1;z++)
                    if(!w.getBlockState(b.add(x,0,z)).isOf(net.minecraft.block.Blocks.GOLD_BLOCK))gold=false;
                if(!gold)continue;
                boolean torches=w.getBlockState(n.north()).isOf(net.minecraft.block.Blocks.REDSTONE_TORCH)
                    &&w.getBlockState(n.south()).isOf(net.minecraft.block.Blocks.REDSTONE_TORCH)
                    &&w.getBlockState(n.east()).isOf(net.minecraft.block.Blocks.REDSTONE_TORCH)
                    &&w.getBlockState(n.west()).isOf(net.minecraft.block.Blocks.REDSTONE_TORCH);
                if(!torches)continue;
                long key=net.minecraft.util.math.ChunkPos.toLong(n.getX(),n.getZ())^(((long)n.getY())<<48);
                if(!w.getBlockState(n.up()).isOf(net.minecraft.block.Blocks.FIRE)) {
                    if(HEROBRINE_WARNED.add(pl.getUuid()))CorisandeManager.say(pl,"I have a very bad feeling about this...",true);
                    continue;
                }
                if(!HEROBRINE_RITUALS.add(key))continue;
                HerobrineEntity h=FromTheHorror.HEROBRINE.create(w);
                if(h!=null){h.refreshPositionAndAngles(n.getX()+0.5,n.getY()+1,n.getZ()+3.5,pl.getYaw(),0);w.spawnEntity(h);
                    w.playSound(null,n,net.minecraft.sound.SoundEvents.ENTITY_WITHER_SPAWN,net.minecraft.sound.SoundCategory.HOSTILE,1.2f,0.45f);
                    for(ServerPlayerEntity player:w.getPlayers())CorisandeManager.say(player,"You lit it. You actually lit it. He's here.",true);}
                return;
            }
        }
    }
'''
if "checkHerobrineRituals(ServerWorld" not in s:s=s.replace("    public static void trigger(ServerWorld w, ServerPlayerEntity p) {",ritual+"\n    public static void trigger(ServerWorld w, ServerPlayerEntity p) {",1)
p.write_text(s)
# Give the altar a genuinely hostile Herobrine which pursues players and damages nearby builds.
(r/"HerobrineEntity.java").write_text("""package com.fromthehorror;
import net.minecraft.block.BlockState;
import net.minecraft.block.Blocks;
import net.minecraft.entity.EntityType;
import net.minecraft.entity.attribute.DefaultAttributeContainer;
import net.minecraft.entity.attribute.EntityAttributes;
import net.minecraft.entity.damage.DamageSource;
import net.minecraft.entity.mob.HostileEntity;
import net.minecraft.entity.player.PlayerEntity;
import net.minecraft.server.world.ServerWorld;
import net.minecraft.sound.SoundCategory;
import net.minecraft.sound.SoundEvents;
import net.minecraft.text.Text;
import net.minecraft.util.math.BlockPos;
import net.minecraft.world.GameRules;
import net.minecraft.world.World;
public class HerobrineEntity extends HostileEntity {
 private int life=20*60*20;
 public HerobrineEntity(EntityType<? extends HostileEntity> type,World world){super(type,world);setPersistent();setCustomName(Text.literal("Herobrine"));setCustomNameVisible(true);}
 public static DefaultAttributeContainer.Builder createAttributes(){return HostileEntity.createHostileAttributes().add(EntityAttributes.GENERIC_MAX_HEALTH,180.0).add(EntityAttributes.GENERIC_MOVEMENT_SPEED,0.38).add(EntityAttributes.GENERIC_ATTACK_DAMAGE,16.0).add(EntityAttributes.GENERIC_FOLLOW_RANGE,96.0).add(EntityAttributes.GENERIC_KNOCKBACK_RESISTANCE,1.0);}
 @Override public void tick(){super.tick();if(getWorld().isClient)return;if(--life<=0){discard();return;}PlayerEntity target=getWorld().getClosestPlayer(this,96.0);if(target==null||target.isSpectator())return;getLookControl().lookAt(target,45f,45f);getNavigation().startMovingTo(target,1.25);if(distanceTo(target)<3.0&&age%18==0)tryAttack(target);if(age%32==0&&getWorld() instanceof ServerWorld sw)destroyNearbyBlock(sw,target);if(age%100==0)getWorld().playSound(null,getBlockPos(),SoundEvents.ENTITY_ENDERMAN_STARE,SoundCategory.HOSTILE,0.9f,0.45f);}
 private void destroyNearbyBlock(ServerWorld world,PlayerEntity target){if(!world.getGameRules().getBoolean(GameRules.DO_MOB_GRIEFING))return;BlockPos c=target.getBlockPos();for(int i=0;i<18;i++){BlockPos p=new BlockPos(c.getX()+random.nextInt(9)-4,c.getY()+random.nextInt(5)-1,c.getZ()+random.nextInt(9)-4);BlockState b=world.getBlockState(p);if(b.isAir()||b.isOf(Blocks.BEDROCK)||b.isOf(Blocks.BARRIER)||b.isOf(Blocks.OBSIDIAN)||b.isOf(Blocks.END_PORTAL)||b.isOf(Blocks.END_PORTAL_FRAME)||b.getHardness(world,p)<0||b.getHardness(world,p)>5||world.getBlockEntity(p)!=null)continue;world.breakBlock(p,true,this);world.playSound(null,p,SoundEvents.BLOCK_STONE_BREAK,SoundCategory.HOSTILE,0.7f,0.55f);break;}}
 @Override public boolean damage(DamageSource source,float amount){return super.damage(source,amount);}
}
""",encoding="utf-8")
# Register the new mob, spawn egg, command target and renderer.
p=r/"FromTheHorror.java";s=p.read_text()
s=s.replace("    public static EntityType<WatcherEntity> WATCHER;","    public static EntityType<WatcherEntity> WATCHER;\n    public static EntityType<HerobrineEntity> HEROBRINE;",1)
s=s.replace("        MAN = Registry.register(Registries.ENTITY_TYPE",'''        HEROBRINE = Registry.register(Registries.ENTITY_TYPE, new Identifier(ID, "herobrine"),
                FabricEntityTypeBuilder.create(SpawnGroup.MONSTER, HerobrineEntity::new)
                        .dimensions(EntityDimensions.fixed(0.7f, 2.5f)).trackRangeBlocks(112).build());
        FabricDefaultAttributeRegistry.register(HEROBRINE, HerobrineEntity.createAttributes());
        MAN = Registry.register(Registries.ENTITY_TYPE''',1)
s=s.replace('Item e2 = egg("watcher", WATCHER, 0x0a0a0c, 0xffffff);','Item e2 = egg("watcher", WATCHER, 0x0a0a0c, 0xffffff);\n        Item herobrineEgg = egg("herobrine", HEROBRINE, 0x080808, 0xffffff);',1)
s=s.replace('e.add(e1); e.add(e2); e.add(e3);','e.add(e1); e.add(e2); e.add(herobrineEgg); e.add(e3);',1)
s=s.replace('DreadDirector.spawn(c.getSource().getWorld(), c.getSource().getPlayerOrThrow(), WATCHER, 20, 26); return 1; }))\n                    .then(CommandManager.literal("corisande")','DreadDirector.spawn(c.getSource().getWorld(), c.getSource().getPlayerOrThrow(), HEROBRINE, 20, 26); return 1; }))\n                    .then(CommandManager.literal("corisande")',1)
p.write_text(s)
p=r/"client/FromTheHorrorClient.java";s=p.read_text()
needle='        EntityRendererRegistry.register(FromTheHorror.WATCHER, ctx -> new FigureRenderer<>(ctx, NfLayers.WATCHER, FigureModel.WATCHER, "watcher", 1.0f));'
if "register(FromTheHorror.HEROBRINE" not in s:s=s.replace(needle,needle+'\n        EntityRendererRegistry.register(FromTheHorror.HEROBRINE, ctx -> new FigureRenderer<>(ctx, NfLayers.WATCHER, FigureModel.WATCHER, "watcher", 1.08f));',1)
p.write_text(s)
# Structures: 10% per newly visited chunk, plus loot chests in both generated sites.
p=r/"NaturalStructures.java";s=p.read_text()
s=s.replace("Math.floorMod((int)(hash^(hash>>>32)),180)","Math.floorMod((int)(hash^(hash>>>32)),20)")
s=s.replace("import net.minecraft.block.Blocks;","import net.minecraft.block.Blocks;\nimport net.minecraft.block.entity.ChestBlockEntity;\nimport net.minecraft.item.ItemStack;\nimport net.minecraft.item.Items;")
s=s.replace("w.setBlockState(p.add(0,1,0),Blocks.CHEST.getDefaultState(),3);","w.setBlockState(p.add(0,1,0),Blocks.CHEST.getDefaultState(),3);\n   fillLoot(w,p.add(0,1,0),true);",1)
s=s.replace("w.setBlockState(p.add(0,3,0),Blocks.SOUL_LANTERN.getDefaultState(),3);","w.setBlockState(p.add(0,3,0),Blocks.SOUL_LANTERN.getDefaultState(),3);\n   w.setBlockState(p.add(2,1,0),Blocks.CHEST.getDefaultState(),3);\n   fillLoot(w,p.add(2,1,0),false);",1)
s=s.replace(" private static void place(ServerWorld w, BlockPos p, boolean cabin){"," private static void place(ServerWorld w, BlockPos p, boolean cabin){",1)
s=s.replace("\n }\n}",'''
 }
 private static void fillLoot(ServerWorld w,BlockPos pos,boolean cabin){
  if(!(w.getBlockEntity(pos) instanceof ChestBlockEntity chest))return;
  chest.setStack(0,new ItemStack(Items.BREAD,3+w.random.nextInt(4)));
  chest.setStack(1,new ItemStack(Items.IRON_INGOT,1+w.random.nextInt(4)));
  chest.setStack(2,new ItemStack(Items.TORCH,8+w.random.nextInt(9)));
  chest.setStack(3,new ItemStack(cabin?Items.GOLDEN_APPLE:Items.DIAMOND,1));
  chest.setStack(4,new ItemStack(Items.ARROW,8+w.random.nextInt(17)));
  chest.setStack(5,new ItemStack(Items.ENDER_PEARL,1+w.random.nextInt(2)));
  chest.setStack(6,new ItemStack(Items.BONE,2+w.random.nextInt(5)));
  chest.markDirty();
 }
}''',1)
p.write_text(s)
print("Oct 31 requested features applied")
