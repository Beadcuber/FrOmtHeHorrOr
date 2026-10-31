package com.fromthehorror;
import net.minecraft.entity.EntityType;
import net.minecraft.entity.attribute.DefaultAttributeContainer;
import net.minecraft.entity.attribute.EntityAttributes;
import net.minecraft.entity.mob.HostileEntity;
import net.minecraft.entity.player.PlayerEntity;
import net.minecraft.server.world.ServerWorld;
import net.minecraft.world.World;
import net.minecraft.sound.SoundEvents;
import net.minecraft.sound.SoundCategory;
import net.minecraft.entity.effect.StatusEffectInstance;
import net.minecraft.entity.effect.StatusEffects;
public class HorrorMobEntity extends HostileEntity {
 private int life=3600, cooldown=100;
 public HorrorMobEntity(EntityType<? extends HostileEntity> type, World world){super(type,world);setPersistent();setCustomName(net.minecraft.text.Text.literal(type==FromTheHorror.LURKER?"The Lurker":type==FromTheHorror.MIMIC?"The Mimic":"The Screecher"));setCustomNameVisible(true);}
 public static DefaultAttributeContainer.Builder createAttributes(){return HostileEntity.createHostileAttributes().add(EntityAttributes.GENERIC_MAX_HEALTH,46).add(EntityAttributes.GENERIC_MOVEMENT_SPEED,.31).add(EntityAttributes.GENERIC_ATTACK_DAMAGE,7).add(EntityAttributes.GENERIC_FOLLOW_RANGE,72);}
 @Override public void tick(){super.tick();if(getWorld().isClient)return;if(--life<=0){discard();return;}PlayerEntity p=getWorld().getClosestPlayer(this,72);if(p==null||p.isSpectator())return;double d=distanceTo(p);if(--cooldown<=0){cooldown=120+random.nextInt(160);if(getType()==FromTheHorror.MIMIC&&d>8&&d<36&&getWorld() instanceof ServerWorld sw){double a=p.getYaw()*Math.PI/180;requestTeleport(p.getX()-Math.sin(a)*9,p.getY(),p.getZ()+Math.cos(a)*9);sw.playSound(null,getBlockPos(),SoundEvents.ENTITY_ENDERMAN_TELEPORT,SoundCategory.HOSTILE,.8f,.55f);}else if(getType()==FromTheHorror.SCREECHER&&d<14){p.addStatusEffect(new StatusEffectInstance(StatusEffects.DARKNESS,70));getWorld().playSound(null,getBlockPos(),SoundEvents.ENTITY_WARDEN_SONIC_BOOM,SoundCategory.HOSTILE,.75f,.55f);}else if(getType()==FromTheHorror.LURKER&&d<30)getWorld().playSound(null,getBlockPos(),SoundEvents.ENTITY_WARDEN_HEARTBEAT,SoundCategory.HOSTILE,.65f,.5f);}if(d<2.2&&age%20==0)tryAttack(p);}
}