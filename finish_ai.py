from pathlib import Path
p=Path('src/main/java/com/fromthehorror/HorrorMobEntity.java')
s=p.read_text()
s=s.replace('import net.minecraft.entity.EntityType;','import net.minecraft.entity.EntityType;\nimport net.minecraft.entity.ai.goal.*;')
s=s.replace('    public static DefaultAttributeContainer.Builder createAttributes() {','    @Override protected void initGoals() {\n        goalSelector.add(0,new SwimGoal(this));\n        goalSelector.add(2,new MeleeAttackGoal(this,1.15,true));\n        goalSelector.add(7,new WanderAroundFarGoal(this,0.8));\n        goalSelector.add(8,new LookAtEntityGoal(this,PlayerEntity.class,24.0f));\n        goalSelector.add(9,new LookAroundGoal(this));\n        targetSelector.add(1,new ActiveTargetGoal<>(this,PlayerEntity.class,true));\n    }\n    public static DefaultAttributeContainer.Builder createAttributes() {')
p.write_text(s)
