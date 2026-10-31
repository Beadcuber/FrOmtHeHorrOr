from pathlib import Path
import json, shutil

root = Path(".")
java = root / "src/main/java/com/fromthehorror"
res = root / "src/main/resources/assets/fromthehorror"
def edit(path, old, new, count=1):
    s = path.read_text(encoding="utf-8")
    if old not in s:
        raise SystemExit("Missing final-fix target in " + str(path) + ": " + old[:100])
    path.write_text(s.replace(old, new, count), encoding="utf-8")

# The cabin and shrine are generated during the server tick, never from CHUNK_LOAD.
(java / "NaturalStructures.java").write_text(r'''package com.fromthehorror;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerTickEvents;
import net.minecraft.block.Blocks;
import net.minecraft.server.world.ServerWorld;
import net.minecraft.world.Heightmap;
import net.minecraft.util.math.BlockPos;
import net.minecraft.util.math.ChunkPos;
import java.util.HashSet;
import java.util.Set;
public final class NaturalStructures {
 private static final Set<Long> DONE = new HashSet<>();
 private NaturalStructures(){}
 public static void register(){
  ServerTickEvents.END_WORLD_TICK.register(w -> {
   for (var player : w.getPlayers()) {
    ChunkPos center = new ChunkPos(player.getBlockPos());
    boolean placed = false;
    for (int dx=-3; dx<=3 && !placed; dx++) for (int dz=-3; dz<=3 && !placed; dz++) {
     int cx=center.x+dx, cz=center.z+dz;
     if (!w.isChunkLoaded(cx,cz)) continue;
     long key = ChunkPos.toLong(cx,cz);
     if (DONE.contains(key)) continue;
     DONE.add(key);
     long hash = cx*341873128712L+cz*132897987541L;
     int pick = Math.floorMod((int)(hash^(hash>>>32)),180);
     if (pick > 1) continue;
     int x=(cx<<4)+8, z=(cz<<4)+8;
     int y=w.getTopY(Heightmap.Type.WORLD_SURFACE,x,z);
     if (y<w.getBottomY()+2 || y>w.getTopY()-12) continue;
     BlockPos p=new BlockPos(x,y,z);
     if (!w.getBlockState(p).isAir()) continue;
     place(w,p,pick==0);
     placed=true;
    }
    if (placed) break;
   }
  });
 }
 private static void place(ServerWorld w, BlockPos p, boolean cabin){
  if(cabin){
   for(int x=-3;x<=3;x++)for(int z=-3;z<=3;z++)w.setBlockState(p.add(x,0,z),Blocks.OAK_PLANKS.getDefaultState(),3);
   for(int y=1;y<=4;y++)for(int x=-3;x<=3;x++)for(int z=-3;z<=3;z++)
    if(Math.abs(x)==3||Math.abs(z)==3) if(!(z==3&&x==0&&y<3))
     w.setBlockState(p.add(x,y,z),(y==4?Blocks.SPRUCE_LOG:Blocks.OAK_PLANKS).getDefaultState(),3);
   for(int x=-3;x<=3;x++)for(int z=-3;z<=3;z++)if(Math.abs(x)+Math.abs(z)>=4)w.setBlockState(p.add(x,5,z),Blocks.DARK_OAK_PLANKS.getDefaultState(),3);
   w.setBlockState(p.add(1,1,1),Blocks.COBWEB.getDefaultState(),3);
   w.setBlockState(p.add(-1,1,-1),Blocks.COBWEB.getDefaultState(),3);
   w.setBlockState(p.add(0,1,0),Blocks.CHEST.getDefaultState(),3);
  } else {
   for(int x=-4;x<=4;x++)for(int z=-4;z<=4;z++)if(Math.abs(x)==4||Math.abs(z)==4)w.setBlockState(p.add(x,0,z),Blocks.CRYING_OBSIDIAN.getDefaultState(),3);
   for(int x=-2;x<=2;x++)for(int z=-2;z<=2;z++)w.setBlockState(p.add(x,0,z),Blocks.POLISHED_BLACKSTONE.getDefaultState(),3);
   for(int[] q:new int[][]{{-3,-3},{-3,3},{3,-3},{3,3}})for(int y=1;y<=3;y++)w.setBlockState(p.add(q[0],y,q[1]),Blocks.POLISHED_BLACKSTONE_BRICKS.getDefaultState(),3);
   w.setBlockState(p.up(),Blocks.REDSTONE_BLOCK.getDefaultState(),3);
   w.setBlockState(p.add(0,2,0),Blocks.CHAIN.getDefaultState(),3);
   w.setBlockState(p.add(0,3,0),Blocks.SOUL_LANTERN.getDefaultState(),3);
  }
 }
}
''', encoding="utf-8")

# Ten-times movement, same 20-tick attack cadence, much stronger hit knockback.
p=java/"HorrorMobEntity.java"
s=p.read_text(encoding="utf-8")
s=s.replace("new MeleeAttackGoal(this,1.15,true)","new MeleeAttackGoal(this,11.5,true)")
s=s.replace(".add(EntityAttributes.GENERIC_MOVEMENT_SPEED, 0.31)",".add(EntityAttributes.GENERIC_MOVEMENT_SPEED, 3.1)")
s=s.replace("if (distance < 2.2 && age % 20 == 0) tryAttack(target);",
"""if (distance < 2.2 && age % 20 == 0 && tryAttack(target)) {
            target.takeKnockback(3.0, target.getX() - getX(), target.getZ() - getZ());
        }""")
p.write_text(s,encoding="utf-8")

# Persist mood and suppress the world entity while Corisande is carried.
p=java/"CorisandeState.java"
s=p.read_text(encoding="utf-8")
s=s.replace("public boolean met, turned, dead, warned, greeted;","public boolean met, turned, dead, warned, greeted, carried;")
s=s.replace('n.putBoolean("warned", warned); n.putBoolean("greeted", greeted);','n.putBoolean("warned", warned); n.putBoolean("greeted", greeted); n.putBoolean("carried", carried);')
s=s.replace('s.warned = n.getBoolean("warned"); s.greeted = n.getBoolean("greeted");','s.warned = n.getBoolean("warned"); s.greeted = n.getBoolean("greeted"); s.carried = n.getBoolean("carried");')
p.write_text(s,encoding="utf-8")

p=java/"CorisandeEntity.java"
s=p.read_text(encoding="utf-8")
s=s.replace('''            carried.getOrCreateNbt().put("CorisandeData",data);
            if(!player.getInventory().insertStack(carried)) {''','''            carried.getOrCreateNbt().put("CorisandeData",data);
            if(!player.getInventory().insertStack(carried)) {''')
s=s.replace('''            player.getInventory().markDirty();
            player.sendMessage(Text.literal("<Corisande> Pocket-sized? ...I suppose this is fine."),false);
            this.discard();''','''            player.getInventory().markDirty();
            CorisandeState state = CorisandeState.get((ServerWorld)this.getWorld());
            state.carried = true;
            state.entity = null;
            state.markDirty();
            player.sendMessage(Text.literal("<Corisande> Pocket-sized? ...I suppose this is fine."),false);
            this.discard();''')
s=s.replace('''        nbt.putBoolean("Hostile", isHostile());
        nbt.putBoolean("Stay", stay);''','''        nbt.putBoolean("Hostile", isHostile());
        nbt.putBoolean("Stay", stay);
        nbt.putInt("Mood", getMood());''')
s=s.replace('''        stay = nbt.getBoolean("Stay");
        if (nbt.getBoolean("Hostile")) turn();''','''        stay = nbt.getBoolean("Stay");
        setMood(nbt.contains("Mood") ? nbt.getInt("Mood") : 0);
        if (nbt.getBoolean("Hostile")) turn();''')
p.write_text(s,encoding="utf-8")

# Redeploying from inventory restores mood and updates the world's single Corisande reference.
p=java/"CorisandeCarryItem.java"
s=p.read_text(encoding="utf-8")
s=s.replace('''            entity.readNbt(data);
            Vec3d look=user.getRotationVec(1.0f);''','''            entity.readNbt(data);
            Vec3d look=user.getRotationVec(1.0f);''')
s=s.replace('''            if(world.spawnEntity(entity)) {
                if(!user.getAbilities().creativeMode) stack.decrement(1);''','''            if(world.spawnEntity(entity)) {
                CorisandeState state = CorisandeState.get((net.minecraft.server.world.ServerWorld)world);
                state.entity = entity.getUuid();
                state.carried = false;
                state.markDirty();
                if(!user.getAbilities().creativeMode) stack.decrement(1);''')
p.write_text(s,encoding="utf-8")

p=java/"CorisandeManager.java"
s=p.read_text(encoding="utf-8")
s=s.replace('''        if ((e == null || e.isRemoved()) && w.getTime() - spawnedAt > 200) spawnNear(w, p, st);''','''        if (!st.carried && (e == null || e.isRemoved()) && w.getTime() - spawnedAt > 200) spawnNear(w, p, st);''')
p.write_text(s,encoding="utf-8")

# The carried item gets a real inventory model and a copy of Corisande's face texture.
models=res/"models/item"
models.mkdir(parents=True,exist_ok=True)
(models/"corisande_carry.json").write_text(json.dumps({"parent":"minecraft:item/generated","textures":{"layer0":"fromthehorror:item/corisande_carry"}},indent=2)+"\n",encoding="utf-8")
shutil.copyfile(res/"textures/entity/corisande_0.png",res/"textures/item/corisande_carry.png")

# Minecraft spawn eggs use the vanilla dynamic two-colour egg renderer; ensure every egg has its model.
for f in (java/"FromTheHorror.java",):
    src=f.read_text(encoding="utf-8")
    import re
    names=sorted(set(re.findall(r'egg\("([a-z0-9_]+)"',src)))
    for name in names:
        (models/(name+"_spawn_egg.json")).write_text('{ "parent": "minecraft:item/template_spawn_egg" }\n',encoding="utf-8")

lang=res/"lang/en_us.json"
d=json.loads(lang.read_text(encoding="utf-8"))
d["item.fromthehorror.corisande_carry"]="Corisande"
lang.write_text(json.dumps(d,indent=2)+"\n",encoding="utf-8")
print("Applied safe structure ticking, monster movement/knockback, Corisande carry/mood persistence, and item models.")
