package com.fromthehorror.forge.client;
import com.fromthehorror.forge.VivianEntity;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.MobRenderer;
import net.minecraft.resources.ResourceLocation;
public class VivianRenderer extends MobRenderer<VivianEntity, VivianModel> {
    private static final ResourceLocation TEXTURE = new ResourceLocation("vivian", "textures/entity/vivian_0.png");
    public VivianRenderer(EntityRendererProvider.Context context) { super(context, new VivianModel(context.bakeLayer(VivianModel.LAYER)), 0.35F); }
    @Override public ResourceLocation getTextureLocation(VivianEntity entity) { return TEXTURE; }
}
