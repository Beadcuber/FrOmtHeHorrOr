from pathlib import Path

root = Path("src/main/java/com/fromthehorror")
root.mkdir(parents=True, exist_ok=True)
(root / "NaturalStructures.java").write_text(r"""package com.fromthehorror;

import net.fabricmc.fabric.api.event.lifecycle.v1.ServerTickEvents;
import net.minecraft.block.Blocks;
import net.minecraft.block.entity.ChestBlockEntity;
import net.minecraft.item.ItemStack;
import net.minecraft.item.Items;
import net.minecraft.server.world.ServerWorld;
import net.minecraft.util.math.BlockPos;
import net.minecraft.util.math.ChunkPos;
import net.minecraft.world.Heightmap;
import net.minecraft.world.World;
import java.util.HashSet;
import java.util.Set;
import java.util.ArrayList;
import java.util.List;
import java.util.Comparator;

/** Places one ThatMob-inspired wooden house and one remote lookout per Overworld save. */
public final class NaturalStructures {
    private static final Set<String> DONE = new HashSet<>();
    private static final List<BlockPos> HOUSES = new ArrayList<>();
    private static final List<BlockPos> TOWERS = new ArrayList<>();
    public static BlockPos nearest(BlockPos from, boolean house) {
        List<BlockPos> sites = house ? HOUSES : TOWERS;
        return sites.stream().min(Comparator.comparingDouble(p -> p.getSquaredDistance(from))).orElse(null);
    }
    private NaturalStructures() {}

    public static void register() {
        ServerTickEvents.END_WORLD_TICK.register(world -> {
            if (!(world instanceof ServerWorld) || world.getRegistryKey() != World.OVERWORLD) return;
            String key = world.getRegistryKey().getValue().toString();
            if (!DONE.add(key)) return;

            // Fixed, seed-derived positions make restarts idempotent: the same two sites are rebuilt.
            long seed = world.getSeed();
            BlockPos spawn = world.getSpawnPos();
            ChunkPos origin = new ChunkPos(spawn);
            double angle = Math.floorMod(seed, 6283L) / 1000.0;
            int radiusA = 26 + (int)Math.floorMod(seed >>> 8, 12L);
            int radiusB = 29 + (int)Math.floorMod(seed >>> 20, 13L);
            int houseX = origin.x + (int)Math.round(Math.cos(angle) * radiusA);
            int houseZ = origin.z + (int)Math.round(Math.sin(angle) * radiusA);
            int towerX = origin.x + (int)Math.round(Math.cos(angle + 2.35) * radiusB);
            int towerZ = origin.z + (int)Math.round(Math.sin(angle + 2.35) * radiusB);

            placeAt(world, houseX, houseZ, true);
            placeAt(world, towerX, towerZ, false);
        });
    }

    private static void placeAt(ServerWorld world, int cx, int cz, boolean house) {
        world.getChunk(cx, cz); // Generate the chosen site once, rather than waiting for a rare random roll.
        int x = (cx << 4) + 8;
        int z = (cz << 4) + 8;
        int y = world.getTopY(Heightmap.Type.MOTION_BLOCKING_NO_LEAVES, x, z);
        if (y < world.getBottomY() + 2 || y > world.getTopY() - 26) return;
        BlockPos base = new BlockPos(x, y, z);
        clear(world, base, house ? 7 : 4, house ? 9 : 22, house ? 6 : 4);
        if (house) buildHouse(world, base);
        else buildWatchtower(world, base);
        (house ? HOUSES : TOWERS).add(base.toImmutable());
    }

    private static void clear(ServerWorld w, BlockPos p, int rx, int height, int rz) {
        for (int x=-rx; x<=rx; x++) for (int z=-rz; z<=rz; z++)
            for (int y=1; y<=height; y++) set(w,p.add(x,y,z),Blocks.AIR);
    }

    private static void buildHouse(ServerWorld w, BlockPos p) {
        // Stone footing and a compact oak cabin with visible log framing and a usable upper loft.
        fill(w,p,-6,0,-5,6,0,5,Blocks.COBBLESTONE);
        fill(w,p,-5,1,-4,5,1,4,Blocks.SPRUCE_PLANKS);
        for (int y=2; y<=6; y++) {
            for (int x=-5; x<=5; x++) for (int z=-4; z<=4; z++) {
                if (Math.abs(x)==5 || Math.abs(z)==4) set(w,p.add(x,y,z),Blocks.OAK_PLANKS);
            }
        }
        for (int x : new int[]{-5,5}) for (int z : new int[]{-4,4})
            fill(w,p,x,2,z,x,7,z,Blocks.SPRUCE_LOG);
        // Front door and windows.
        for (int y=2; y<=3; y++) set(w,p.add(0,y,4),Blocks.AIR);
        for (int x : new int[]{-3,-2,2,3}) {
            set(w,p.add(x,3,-4),Blocks.GLASS_PANE);
            set(w,p.add(x,3,4),Blocks.GLASS_PANE);
        }
        for (int z : new int[]{-2,-1,1,2}) {
            set(w,p.add(-5,3,z),Blocks.GLASS_PANE);
            set(w,p.add(5,3,z),Blocks.GLASS_PANE);
        }
        // Upper floor and loft access.
        fill(w,p,-4,4,-3,4,4,3,Blocks.SPRUCE_PLANKS);
        set(w,p.add(0,4,0),Blocks.AIR);
        fill(w,p,-5,7,-4,5,7,4,Blocks.DARK_OAK_PLANKS);
        for (int x=-4; x<=4; x++) {
            set(w,p.add(x,8,-3+Math.abs(x)/2),Blocks.DARK_OAK_PLANKS);
            set(w,p.add(x,8,3-Math.abs(x)/2),Blocks.DARK_OAK_PLANKS);
        }
        for (int z=-3; z<=3; z++) {
            set(w,p.add(-4+Math.abs(z)/2,8,z),Blocks.DARK_OAK_PLANKS);
            set(w,p.add(4-Math.abs(z)/2,8,z),Blocks.DARK_OAK_PLANKS);
        }
        fill(w,p,-1,2,-3,1,2,-3,Blocks.BOOKSHELF);
        set(w,p.add(-3,2,-2),Blocks.CRAFTING_TABLE);
        set(w,p.add(3,2,-2),Blocks.FURNACE);
        set(w,p.add(-2,2,2),Blocks.COBWEB);
        set(w,p.add(2,2,2),Blocks.COBWEB);
        set(w,p.add(0,5,0),Blocks.LANTERN);
        set(w,p.add(0,8,0),Blocks.CHAIN);
        set(w,p.add(0,9,0),Blocks.SOUL_LANTERN);
        set(w,p.add(2,2,0),Blocks.CHEST);
        fillChest(w,p.add(2,2,0),true);
        set(w,p.add(-2,5,0),Blocks.CHEST);
        fillChest(w,p.add(-2,5,0),false);
        // A small porch.
        fill(w,p,-2,1,5,2,1,7,Blocks.SPRUCE_PLANKS);
        for (int x : new int[]{-2,2}) {
            fill(w,p,x,2,6,x,3,6,Blocks.SPRUCE_FENCE);
            set(w,p.add(x,4,6),Blocks.LANTERN);
        }
    }

    private static void buildWatchtower(ServerWorld w, BlockPos p) {
        // Tall timber lookout with a lantern crown and an exposed observation deck.
        fill(w,p,-4,0,-4,4,0,4,Blocks.COBBLESTONE);
        for (int[] c : new int[][]{{-3,-3},{-3,3},{3,-3},{3,3}}) {
            fill(w,p,c[0],1,c[1],c[0],18,c[1],Blocks.SPRUCE_LOG);
        }
        for (int y : new int[]{7,14}) {
            fill(w,p,-3,y,-3,3,y,3,Blocks.SPRUCE_PLANKS);
            for (int x=-3; x<=3; x++) for (int z=-3; z<=3; z++)
                if (Math.abs(x)==3 || Math.abs(z)==3) set(w,p.add(x,y+1,z),Blocks.SPRUCE_FENCE);
        }
        // Climbable ladder on the south-facing support.
        for (int y=1; y<=17; y++) set(w,p.add(0,y,3),Blocks.LADDER);
        fill(w,p,-4,19,-4,4,19,4,Blocks.DARK_OAK_PLANKS);
        for (int x=-3; x<=3; x++) for (int z=-3; z<=3; z++)
            if (Math.abs(x)==3 || Math.abs(z)==3) set(w,p.add(x,20,z),Blocks.DARK_OAK_FENCE);
        fill(w,p,-2,21,-2,2,21,2,Blocks.DARK_OAK_PLANKS);
        set(w,p.add(0,22,0),Blocks.SOUL_LANTERN);
        set(w,p.add(0,18,0),Blocks.CHEST);
        fillChest(w,p.add(0,18,0),false);
        for (int[] c : new int[][]{{-3,-3},{-3,3},{3,-3},{3,3}})
            set(w,p.add(c[0],19,c[1]),Blocks.LANTERN);
    }

    private static void fillChest(ServerWorld w, BlockPos p, boolean house) {
        if (!(w.getBlockEntity(p) instanceof ChestBlockEntity chest)) return;
        chest.setStack(0,new ItemStack(Items.BREAD,house ? 4 : 2));
        chest.setStack(1,new ItemStack(Items.TORCH,house ? 12 : 8));
        chest.setStack(2,new ItemStack(Items.IRON_INGOT,house ? 2 : 4));
        chest.setStack(3,new ItemStack(Items.ARROW,house ? 4 : 12));
        chest.markDirty();
    }

    private static void fill(ServerWorld w, BlockPos p, int x1,int y1,int z1,int x2,int y2,int z2, net.minecraft.block.Block block) {
        for(int x=x1;x<=x2;x++) for(int y=y1;y<=y2;y++) for(int z=z1;z<=z2;z++) set(w,p.add(x,y,z),block);
    }
    private static void set(ServerWorld w, BlockPos p, net.minecraft.block.Block block) {
        w.setBlockState(p,block.getDefaultState(),3);
    }
}
""", encoding="utf-8")
print("Wrote Vivian-inspired house and watchtower generator.")
