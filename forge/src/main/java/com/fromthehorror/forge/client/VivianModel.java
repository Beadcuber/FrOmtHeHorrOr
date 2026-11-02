package com.fromthehorror.forge.client;
import com.fromthehorror.forge.VivianEntity;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.model.geom.ModelLayerLocation;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.model.geom.PartPose;
import net.minecraft.client.model.geom.builders.CubeListBuilder;
import net.minecraft.client.model.geom.builders.LayerDefinition;
import net.minecraft.client.model.geom.builders.MeshDefinition;
import net.minecraft.client.model.geom.builders.PartDefinition;
import net.minecraft.resources.ResourceLocation;
public class VivianModel extends EntityModel<VivianEntity> {
    public static final ModelLayerLocation LAYER = new ModelLayerLocation(new ResourceLocation("vivian", "vivian"), "main");
    private final ModelPart orb;
    public VivianModel(ModelPart root) { orb = root.getChild("orb"); }
    public static LayerDefinition createLayer() {
        MeshDefinition mesh = new MeshDefinition(); PartDefinition root = mesh.getRoot();
        root.addOrReplaceChild("orb", CubeListBuilder.create().texOffs(0,0).addBox(-4,-4,-4,8,8,8), PartPose.ZERO);
        return LayerDefinition.create(mesh, 64, 64);
    }
    @Override public void setupAnim(VivianEntity entity, float a, float b, float age, float yaw, float pitch) { orb.y = (float)Math.sin(age * 0.12F) * 0.15F; }
    @Override public void renderToBuffer(PoseStack pose, VertexConsumer buffer, int light, int overlay, float r, float g, float b, float alpha) { orb.render(pose, buffer, light, overlay, r, g, b, alpha); }
}
