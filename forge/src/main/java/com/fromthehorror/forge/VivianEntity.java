package com.fromthehorror.forge;

import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.PathfinderMob;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.control.FlyingMoveControl;
import net.minecraft.world.entity.ai.navigation.FlyingPathNavigation;
import net.minecraft.world.entity.ai.navigation.PathNavigation;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;

public class VivianEntity extends PathfinderMob {
    private boolean hostile;
    public VivianEntity(EntityType<? extends PathfinderMob> type, Level level) {
        super(type, level);
        this.moveControl = new FlyingMoveControl(this, 20, true);
        this.setNoGravity(true); this.setPersistenceRequired();
        this.setCustomName(net.minecraft.network.chat.Component.literal("Vivian")); this.setCustomNameVisible(true);
        this.hostile = type == VivianForge.VIVIAN_MONSTER.get();
        if (hostile) setHostile(true);
    }
    public static AttributeSupplier.Builder createAttributes() {
        return PathfinderMob.createMobAttributes().add(Attributes.MAX_HEALTH, 20.0D).add(Attributes.MOVEMENT_SPEED, 0.30D)
            .add(Attributes.FLYING_SPEED, 0.50D).add(Attributes.ATTACK_DAMAGE, 18.0D).add(Attributes.FOLLOW_RANGE, 64.0D);
    }
    public boolean isHostile() { return hostile; }
    public void setHostile(boolean value) {
        hostile = value;
        if (value && getAttribute(Attributes.MAX_HEALTH) != null) {
            getAttribute(Attributes.MAX_HEALTH).setBaseValue(100.0D);
            getAttribute(Attributes.MOVEMENT_SPEED).setBaseValue(0.82D);
            getAttribute(Attributes.FLYING_SPEED).setBaseValue(1.45D);
            getAttribute(Attributes.ATTACK_DAMAGE).setBaseValue(26.0D);
            setHealth(100.0F); refreshDimensions();
        }
    }
    @Override protected PathNavigation createNavigation(Level level) { return new FlyingPathNavigation(this, level); }
    @Override public void tick() {
        super.tick();
        if (level().isClientSide) return;
        Player player = level().getNearestPlayer(this, 64.0D);
        if (player == null || player.isSpectator()) return;
        double distance = distanceTo(player);
        if (!hostile) {
            if (distance > 4.0D) getNavigation().moveTo(player, distance > 28.0D ? 1.25D : 1.0D);
            else getNavigation().stop();
        } else {
            getNavigation().moveTo(player, 2.35D);
            if (distance < 3.5D && tickCount % 10 == 0) doHurtTarget(player);
        }
        if (tickCount % 8 == 0) {
            Vec3 p = position().add(0, 0.5, 0);
            level().addParticle(hostile ? net.minecraft.core.particles.ParticleTypes.SOUL_FIRE_FLAME : net.minecraft.core.particles.ParticleTypes.END_ROD, p.x, p.y, p.z, 0, 0.01, 0);
        }
    }
}
