package com.fromthehorror.forge.client;
import com.fromthehorror.forge.VivianForge;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.EntityRenderersEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
@Mod.EventBusSubscriber(modid = VivianForge.MOD_ID, bus = Mod.EventBusSubscriber.Bus.MOD, value = Dist.CLIENT)
public final class VivianClient {
    @SubscribeEvent public static void registerLayers(EntityRenderersEvent.RegisterLayerDefinitions event) { event.registerLayerDefinition(VivianModel.LAYER, VivianModel::createLayer); }
    @SubscribeEvent public static void registerRenderers(EntityRenderersEvent.RegisterRenderers event) {
        event.registerEntityRenderer(VivianForge.VIVIAN.get(), VivianRenderer::new);
        event.registerEntityRenderer(VivianForge.VIVIAN_MONSTER.get(), VivianRenderer::new);
    }
}
