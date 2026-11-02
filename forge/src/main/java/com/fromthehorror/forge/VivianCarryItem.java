package com.fromthehorror.forge;

import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;

public class VivianCarryItem extends Item {
    public VivianCarryItem(Properties properties) { super(properties); }
    @Override public InteractionResultHolder<ItemStack> use(Level level, Player player, net.minecraft.world.InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        if (!level.isClientSide) {
            VivianEntity entity = VivianForge.VIVIAN.get().create(level);
            if (entity != null) {
                entity.moveTo(player.getX() + 1.5, player.getY() + 1, player.getZ() + 1.5, player.getYRot(), 0);
                level.addFreshEntity(entity);
                if (!player.getAbilities().instabuild) stack.shrink(1);
            }
        }
        return InteractionResultHolder.sidedSuccess(stack, level.isClientSide);
    }
}
